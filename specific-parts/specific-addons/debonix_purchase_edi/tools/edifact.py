#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import logging
import pystache
import simplejson

DEBUG = False

BASE = '/home/cjacquin/debonix/debonix_purchase_edi'
SPEC = os.path.join(BASE, 'doc/debonix.pdf')

PAGE_FOOTER = '(\x0c)?Maquette : ' + \
              'STD Flux de commande DEBONIX - v1.6 ( *) Page : (\d+)/(\d+)'

_logger = logging.getLogger('.'.join(__name__.split('.')[-1:]))


class Debonix(object):
    """
    PDF Spec reader for debonix
    """
    PAGE = re.compile(PAGE_FOOTER)
    SUBSECTION = re.compile('^(?:\x0c)?(\d+\.\d+\.) (.*) \(([^)]+)\)$')
    SECTION = re.compile('^(?:\x0c)?(\d+\.) (.*)$')

    def __init__(self):
        self.path = None
        self.sections = []
        self.content = []
        self.current_section = None
        self.current_subsection = None
        self.spec = None

        self.template =  None
        self.fields =  None
        self.line_fields =  None

    @staticmethod
    def fromjson(json):
        template =  json['template']
        fields = json['fields']
        line_fields =  json['line_fields']

        doc = Debonix()
        doc.spec =  Section('0', 'format from json')
        #doc.spec.sections = sections
        doc.template = template
        doc.fields =  dict((name, FixedField.from_dict(value)) for (name, value)
                           in fields.items())
        doc.line_fields = dict((name, FixedField.from_dict(value)) for (name, value)
                               in line_fields.items())
        return doc

    def tojson(self):
        fields =  dict((name,  value.as_dict()) for (name,  value) in self.fields.items())
        line_fields =  dict((name,  value.as_dict()) for (name,  value) in self.line_fields.items())
        return { 'template': self.template,
                 'fields':  fields,
                 'line_fields':  line_fields
        }

    def build_templates(self):
        if self.spec:
            return
        self._parse_spec(SPEC)
        assert self.spec

        path = os.path.join(BASE, 'doc/CF1504233161.edi')
        records, samples, \
            template = self.readfile(path, for_template=True)
        for s in self.spec.sections:
            assert s.records

        fields = {}
        line_fields = {}
        _logger.warn('SPEC %r' % self.spec)
        for i, section in enumerate(self.spec.sections):
            _logger.warn('SPEC-SECTION %r' % section)
            section.sanity_check()
            if section.code == '160':
                section.template = '{{#commentaire}}160    A{{.}}\r\n' + \
                                   '{{/commentaire}}'
            if section.code == '200':
                section.template = '{{#__lines__}}%s{{/__lines__}}' % \
                                   section.template
            for name, var in section.get_vars():
                if section.code == '200':
                    line_fields[name] = var
                else:
                    fields.setdefault(name, []).append(var)

        for (name, duplicates) in fields.items():
            if len(duplicates) > 1:
                _logger.debug('multiple occurrences of field %r' % name)
                _logger.debug('duplicates %r' % duplicates)
                first = v = duplicates[0]
                others = duplicates[1:]
                while others:
                    assert v.size == others[0].size
                    assert v.type_ == others[0].type_
                    v, others = others[0], others[1:]

            fields[name] = duplicates[0]

        self.template = ''.join(section.template for
                                section in self.spec.sections)
        self.fields = fields
        self.line_fields = line_fields

    def _encode(self, data, fields):
        #fields = self.fields if not line else self.line_fields
        data = data.copy()
        for name, var in fields.items():
            val = data[name]
            encoded = var.encode(val)
            _logger.debug('FORMAT [%s]([%r) -> %r' % (name, val, encoded))
            data[name] = encoded
        return data

    def render(self, data):

        self.build_templates()
        data = self._encode(data, self.fields)
        data['__lines__'] = [self._encode(line, self.line_fields)
                             for line in data['__lines__']]

        message = pystache.render(self.template, data)
        return message

    def accept_spec_line(self, line, container):
        """ accept a line from the pdf document """

        if line == '\n':
            return container
        _logger.debug('DEBONIX ACCEPT [%s][%s]' % (container, line))
        match = None
        for name, matcher in (('page', self.PAGE), ('section', self.SECTION),
                              ('subsection', self.SUBSECTION)):
            match = matcher.match(line)
            if match:
                _logger.debug('MATCHED [%s] %s' % (name, match.groups()))
                if name == 'page':
                    break
                elif name == 'section':
                    container = self.make_section(*match.groups())
                    self.current_section = container
                    break
                elif name == 'subsection':
                    subsection = self.make_subsection(*match.groups())
                    container = subsection
                    break
        if not match:
            _logger.debug('FALLBACK')
            container.content.append(line)
        return container

    def _parse_spec(self, path):
        assert not self.spec

        self.path = path
        self.content = []
        noext, ext = os.path.splitext(path)
        if ext == '.pdf':
            status = os.system('pdftotext -f 5 -layout %s' % path)
            if status != 0:
                raise Exception('could not convert spec to text')
            path = noext + '.txt'

        container = self
        with open(path) as lines:
            for line in lines.readlines():
                _logger.debug('CONTAINER: %s' % container)
                container = self.accept_spec_line(line, container)

        self.spec = self.sections[2]
        return self

    def make_section(self, index, title):
        section = Section(index, title)
        self.content.append(section)
        self.sections.append(section)
        return section

    def make_subsection(self, index, title, code):
        sub = SubSection(index, title, code)
        sub.code = code
        self.current_section.content.append(sub)
        self.current_section.sections.append(sub)
        return sub

    def readfile(self, path, samples={}, locale='latin1', for_template=False):
        if not self.spec:
            self.build_templates()
        spec = self.sections[2]
        d = dict((s.get_spec()[0].value, s) for s in spec.sections)

        samples = {}
        records = []
        templates = []
        with open(path) as lines:
            for line in lines.readlines():
                linespec = d[line[:3]]
                values, _, subtemplate = linespec.extract_line(line,
                                                               samples,
                                                               locale,
                                                               for_template)
                records.append(values)
                templates.append(subtemplate)
        template = ''.join(templates)
        return records, samples, template


class DebonixFieldSpec:

    def __init__(self, name, pattern, convert=lambda v: v):
        self.name = name
        self.pattern = pattern
        self.regex = re.compile(self.make_re())
        self._converter = convert

    def __repr__(self):
        return '<DebonixFieldSpec %s>' % self.name

    def make_re(self):
        return '(?P<%s>%s)' % (self.name, self.pattern)

    def convert(self, string):
        return self._converter(string)


class MatchError(Exception):
    pass


class LinePattern:

    def __init__(self, name, fields, lastopt=False):
        self.name = name
        self.fields = fields
        self.field_dict = dict((f.name, f) for f in fields)
        self.regex = self.assemble(lastopt=lastopt)

    def __repr__(self):
        return '<LP %s>' % self.name

    def assemble(self, fields=None, lastopt=False):
        fields = fields if fields else self.fields
        if lastopt:
            f, l = fields[:-1], fields[-1]
            e = '(?: *)'.join(['(?: +)'.join(p.make_re() for p in f),
                               l.make_re()])
        else:
            e = '(?: +)'.join(f.make_re() for f in fields)
        e = '^' + e + '$'
        return re.compile(e)

    def match(self, line):
        try:
            rec = self.regex.match(line).groupdict()
        except AttributeError:
            raise MatchError(line)
        else:
            return dict((key, self.field_dict[key].convert(value))
                        for (key, value) in rec.items())


class FixedField(object):
    """ FixedField represents a field in a fixed data format like EDIFACT ones """

    def __init__(self, name=None, required=False, type_='N', size=0, offset=0, value=None,
                 comment='', note=None):
        self.name = name
        self.required = required
        self.type_ = type_
        self.size = size
        self.offset = offset
        self.value = value
        self.comment = comment
        self.note = note

    def is_variable(self):
        return self.value.startswith('$')

    def get_varname(self):
        if not self.is_variable():
            return None
        name = self.value[1:]
        # FIXME
        if name[-1] == ']':
            name = name[:-1]
        return name

    def gen_template(self):
        """ generate a template for this field """
        if self.is_variable():
            var = self.get_varname()

        elif self.value == '[Vide]':  # (FIXME) debonix specific, move away
            var = "''"
        elif isinstance(self.value, (str, unicode)):
            if len(self.value) == self.size: # string values
                return self.value
            var = "'%s'" % self.value
        else:
            var = self.value
        if self.type_ == 'N':
            return "{{rj %s %s '0'}}" % (var, self.size)
        elif self.type_ in ('AN', 'A'):
            return "{{lj %s %s}}" % (var, self.size)
        else:
            raise AssertionError("unkown field type %r" % self.type_)

    def __repr__(self):
        return '<%s %s [%s:%s+%s]>' % (self.__class__.__name__, self.name,
                                       self.offset,
                                       self.offset, self.size)

    def encode(self, val):
        raise NotImplementedError

    def extract_field(self, line):
        return line[self.offset:self.offset+self.size]

    def as_dict(self):
        return dict((name, value)
                    for (name, value) in ((name,  getattr(self,  name))
                            for name in dir(self)
                            if not name.startswith('_') and
                            not callable(getattr(self, name))
                    ))

    @staticmethod
    def from_dict(json):
        type_ =  json['type_']
        if type_ ==  'N':
            return Numeric( ** json)
        elif type_ ==  'AN':
            return Alphanum( ** json)
        elif type_ ==  'A':
            return Alpha( ** json)
        else:
            raise ValueError("bad field type")

class Alphanum(FixedField):

    def encode(self, val):
        _logger.debug('AN:encode(%r)' % val)
        raw = unicode(val)
        if len(raw) > self.size:
            #raise ValueError(val)
            _logger.warn('value for %r is truncated' % self.get_varname())
            raw =  raw[:self.size]
        if self.get_varname() == 'commentaire' and not val:  # FIXME
            return ''
        return raw.ljust(self.size)


class Numeric(FixedField):

    def encode(self, val):
        _logger.debug('N:encode(%r)' % val)
        raw = unicode(val)
        if len(raw) > self.size:
            raise ValueError(val)
        return raw.rjust(self.size, '0')


class Alpha(FixedField):

    def encode(self, val):
        _logger.debug('AN:encode(%r)' % val)
        raw = unicode(val)
        if len(raw) > self.size:
            raise ValueError(val)
        return raw.ljust(self.size)

def make_field(name, type_, size, offset, value,
               required=False, comment=None, note=None):
    return {'AN': Alphanum,
            'A': Alpha,
            'N': Numeric}[type_](name, required, type_,
                                 size, offset, value, comment, note)

class Section(object):
    # TODO: this class is to big. Extract doc parser.

    HEADER = re.compile(
        u'(Nom *)(O/F *)(Type *)(Taille *)(Offset *)(Valeur\n)')
    FIELDS = [DebonixFieldSpec('name', '[^$]*', lambda s: s.strip()),
              DebonixFieldSpec('required', 'O|F', lambda s: s == 'O'),
              DebonixFieldSpec('type_', 'N|(?:AN?)', lambda s: s),
              DebonixFieldSpec('size', '\d+', lambda s: int(s)),
              DebonixFieldSpec('offset', '\d+', lambda s: int(s)-1),
              DebonixFieldSpec('value', '[^()]+', lambda s: s.strip()),
              DebonixFieldSpec('comment', '(?: *\([^()]+\))?', lambda s: s)]

    NOTE_FIELD = DebonixFieldSpec('note', 'Note :.*', lambda s: s.strip())

    FULL_LINE = LinePattern('full', FIELDS, lastopt=True)
    NAME_VALUE = LinePattern(
        'name&value', [FIELDS[0], FIELDS[-2], FIELDS[-1]], lastopt=True)
    NO_VALUE = LinePattern('novalue', FIELDS[:-2])
    NAME_ONLY = LinePattern('nameonly', [FIELDS[0]])
    NOTE_LINE = LinePattern('notestart', [FIELDS[0], NOTE_FIELD])

    OPEN_COMMENT = LinePattern('opencomment',
                               [FIELDS[0], FIELDS[-2],
                                DebonixFieldSpec('note',
                                                 '(?: *\([^()]+)?',
                                                 lambda s: s)])

    CLOSE_COMMENT = LinePattern('closecomment',
                                FIELDS[:-1] +
                                [DebonixFieldSpec('note',
                                                  '(?: *[^()]+\))?',
                                                  lambda s: s)])

    MISSING_REQ = LinePattern('missing', FIELDS[:1] + FIELDS[2:], lastopt=True)

    LEGEND = LinePattern('legend',
                         [DebonixFieldSpec('key',
                                           '[A-Za-z/\x0c]+'),
                          DebonixFieldSpec('eq', '='),
                          DebonixFieldSpec('desc', '.*')])

    def __init__(self, index, title, fields=None):
        self.index = index
        self.title = title
        self.content = []
        self.sections = []
        self.fields = fields if fields else self.FIELDS
        self.field_dict = dict((f.name, f) for f in self.fields)

        self.have_note = None
        self.records = None

    def __repr__(self):
        return '<%s %s %r>' % (self.__class__.__name__,
                               self.index, self.title)

    def merge_text(self, previous, current):
        if previous and current:
            current = ' '.join((previous, current))
        elif previous:
            current = previous
        return current

    def merge_recs(self, last, rec):
        del rec['__proto__']
        name = self.merge_text(last['name'], rec.get('name', ''))
        notes = self.merge_text(last.get('note', ''), rec.get('note', ''))
        last.update(rec)
        last['name'] = name
        if notes:
            last['note'] = notes


    def extract_line(self, line, samples, locale='latin1', for_template=False):
        _logger.info('EXTRACT LINE[%s] %s' % (for_template, self))
        values = []
        for i in range(len(self.records)):
            field = self.records[i]
            value = field.extract_field(line)
            _logger.debug('EXTRACT[%d][%s][%r]' % (i, field, value))
            try:
                value.decode('ascii')
            except UnicodeDecodeError:
                value = value.decode(locale)

            if field.is_variable():
                samples[field.get_varname()] = value

            if for_template and field.is_variable():
                values.append('{{%s}}' % field.get_varname())
            else:
                values.append(value)

        template = ''.join(values) + '\r\n'
        if for_template:
            self.template = template
        return values, samples, ''.join(values) + '\r\n'

    def sanity_check(self):
        sizes = [f.size for f in self.get_spec()]
        offsets = [f.offset for f in self.get_spec()]
        assert [sum(sizes[:i]) for i in range(len(sizes))] == offsets

    def convert_to_objects(self):
        for rec in self.reassemble_partial_lines():
            del rec['__proto__']
            yield make_field(**rec)

    def reassemble_partial_lines(self):
        last = None
        inside_note = False
        note_start = False

        for rec in self.parse_content():
            proto = rec['__proto__']

            if proto == 'full':

                if inside_note and note_start:
                    assert last
                    note_start = False
                    rec['note'] = rec['value']
                    del rec['value']
                    self.merge_recs(last, rec)
                else:
                    if inside_note:
                        inside_note = False
                    if last:
                        yield last
                    last = rec

            elif proto == 'name&value':

                if inside_note:
                    # pdb.set_trace()
                    assert last
                    if rec['value'].startswith('$'):
                        # must be a new record
                        yield last
                        last = rec
                        inside_note = False
                    else:
                        # must be a continuation of old one
                        note = self.merge_text(rec['name'], rec['value'])
                        del rec['name']
                        del rec['value']
                        rec['note'] = note
                        self.merge_recs(last, rec)
                else:
                    if not last:
                        last = rec
                    else:
                        if last['__proto__'] == 'name&value':
                            rec['name'] = self.merge_text(rec['name'],
                                                          rec['value'])
                            del rec['value']
                            self.merge_recs(last, rec)
                        else:
                            assert last
                            yield last
                            last = rec

            elif proto == 'novalue':

                assert last
                self.merge_recs(last, rec)
                yield last
                last = None

            elif proto == 'nameonly':

                assert last
                if inside_note:
                    assert 'note' not in rec
                    rec['note'] = rec['name']
                    del rec['name']
                    self.merge_recs(last, rec)

                else:
                    self.merge_recs(last, rec)

            elif proto == 'notestart':

                # pdb.set_trace()
                inside_note = True
                note_start = True
                if last:
                    self.merge_recs(last, rec)
                else:
                    assert 0 == 1

            elif proto == 'legend':
                if last:
                    yield last
                    last = None

            elif proto == 'opencomment':
                inside_note = True
                if last:
                    yield last
                inside_note = True
                last = rec

            elif proto == 'closecomment':
                cont = rec['value']
                note = rec['note']
                del rec['value']
                note = cont + ' ' + note
                rec['note'] = note
                self.merge_recs(last, rec)
                yield last
                last = None

            elif proto == 'missing':
                if last:
                    yield last
                last = rec
        if last:
            yield last

    def parse_content(self):
        for i, l in enumerate(self.content[1:]):
            processed = False
            if l == '\n':
                continue
            _logger.debug('LINE [%r]' % l)
            for p in (Section.FULL_LINE, Section.NO_VALUE,
                      Section.NOTE_LINE, Section.LEGEND, Section.MISSING_REQ,
                      Section.NAME_VALUE, Section.OPEN_COMMENT,
                      Section.CLOSE_COMMENT, Section.NAME_ONLY):
                try:
                    _logger.debug('PROBE [%r]' % p)
                    rec = p.match(l)
                    processed = True
                    rec['__proto__'] = p.name
                    if DEBUG:
                        _logger.debug('MATCHED [%s] %s' % (p.name, rec))
                    yield rec
                    break
                except MatchError:
                    pass
            if not processed:
                raise MatchError(l)


class SubSection(Section):

    def __init__(self, index, title, code, fields=None):
        super(SubSection, self).__init__(index, title)
        self.code = code
        if fields:
            self.records =  fields

    def get_spec(self):
        if self.records is None:
            self.records = list(self.convert_to_objects())
        return self.records[:]

    def get_vars(self):
        return [(f.get_varname(), f)
                for f in self.get_spec() if f.value.startswith('$')]

    def __repr__(self):
        return '<%s %s %r (%s)>' % (self.__class__.__name__,
                                    self.index, self.title, self.code)

    def as_dict(self):
        return {'index': self.index,
                'title': self.title,
                'code': self.code,
                'fields': [field.as_dict() for field in self.records] }

    @staticmethod
    def from_dict(data):
        return SubSection(data['index'],  data['title'],  data['code'],
                          [FixedField.from_dict(f) for f in data['fields']])


def rpc_read_edifact(po_name, user='admin', password='admin',
                     dbname='debonix_edi', port=8501):
    import oerplib
    oerp = oerplib.OERP('localhost', protocol='xmlrpc', port=port)

    # Login (the object returned is a browsable record)
    user = oerp.login(user, password, dbname)

    po = oerp.get('purchase.order')
    po_ids = po.search([('name', '=', po_name)])
    if not po_ids:
        raise ValueError("Purchase order %s not found" % po_name)
    for order in po.browse(po_ids):
        record = {}

        # $dateCmd = preg_split('/ /',$donnees->create_date);
        # $heureCmd = preg_replace('/:/','',$dateCmd[1]);
        # $heureCmd = substr($heureCmd,0,6);
        # $dateCmd = preg_replace('/-/','',$dateCmd[0]);

        # addDEB Paramètres : code filiale, siret filiale, date cmd , heure cmd
        # //$cmd->addDEB("DR","42482122100282",$dateCmd,$heureCmd);
        # $cmd->addDEB("PLN","52789590800012",$dateCmd,$heureCmd);

        record['codefiliale'] = 'PLN'
        record['siretFiliale'] = '52789590800012'
        # no acces to record creation datetime ...
        # date = order.create_date.date()
        # heure = order.create_date.time()
        record['dateCmd'] = order.date_order.strftime('%Y%m%d')
        #record['heureCmd'] = order.create_date.time()
        #record['heureCmd'] = datetime.datetime.now().time().strftime('%H%M%S')
        record['heureCmd'] = '090420'

        # DMS
        # addDMS Paramètres : code agence, siret agence, siret debonix
        # //$cmd->addDMS("000","42482122100027","00000540599990");
        # $cmd->addDMS("928","52789590800012","49039922700035");
        record['codeAgence'] = '928'
        record['siretAgence'] = '52789590800012'
        record['siretDebonix'] = '49039922700035'

        # 100
        # add100 Paramètres : compte Debonix, numéro de commande, reference de la commande, date de livraison souhaitée 
        # //$cmd->add100("0000980572",$donnees->name,$donnees->name,$dateLivraison);
        # $cmd->add100("0000175000",$donnees->name,$donnees->name,$dateLivraison);
        record['noCmd'] = order.name
        record['refCmd'] = order.name
        record['dateLiv'] = order.minimum_planned_date.strftime('%Y%m%d')
        record['compteDebonix'] = '0000175000'


        # 140
        # add140 Paramètres : champ adr1,adr2,adr3,adr4,adr5, code postal, ville, tel, fax 
        # (empty($donnees->street2)) ? $street2 ="" : $street2 = $donnees->street2;
        # (empty($donnees->fax)) ? $fax ="" : $fax =$donnees->fax;
        # $cmd->add130(utf8_decode($donnees->client),
        #    "",
        #    utf8_decode($donnees->street),
        #    utf8_decode($street2),
        #    "",
        #    utf8_decode($donnees->zip),
        #    utf8_decode($donnees->city),
        #    utf8_decode($donnees->phone),
        #    utf8_decode($fax));
        # $cmd->add140(utf8_decode($donnees->client),"",utf8_decode($donnees->street),utf8_decode($street2),"",utf8_decode($donnees->zip),utf8_decode($donnees->city),utf8_decode($donnees->phone),utf8_decode($fax));
        record['adr1'] = order.dest_address_id.name
        record['adr2'] = ''
        record['adr3'] = order.dest_address_id.street
        record['adr4'] = ''
        record['adr5'] = ''
        record['cp'] = order.dest_address_id.zip
        record['ville'] = order.dest_address_id.city
        record['tel'] = order.dest_address_id.phone
        fax = order.dest_address_id.fax
        if fax:
            record['fax'] = fax
        else:
            record['fax'] = ''
        # add160 Paramètres : commentaire
        # if($donnees->notes) $cmd->add160(utf8_decode($donnees->notes));
        if order.notes:
            record['commentaire'] = order.notes
        else:
            record['commentaire'] = ''
        order_lines = list(order.order_line)
        lines = []

        def convert_unit(name):
            if name == 'PCE':
                return 'P'
            assert 0 == 1

        totalQty = 0
        totalHT = 0
        for line_index, order_line in enumerate(order_lines):
            line = {}
            line['codag'] = order_line.product_id.code
            line['libelle'] = order_line.product_id.name[:70]
            line['prixUnitaireNet'] = pu = int(order_line.price_unit * 10000)

            # call for behave
            # La quantité doit tenir compte du conditionnement remonté dans
            # le champ Quantity du catalogue.
            #
            # Si un client saisie 10 en quantité
            #  sur le site et que le conditionnement présent dans le
            #  champs quantity = 200,  la quantité sera égal  2000 * 1000'
            line['qte'] = qty = int(order_line.product_qty * 1000)

            line['refarticleFournisseur'] = order_line.product_id.code
            line['ligne'] = line_index+1
            line['montantLigne'] = montant = int(order_line.price_subtotal * 1000)

            totalHT += (pu * montant)
            totalQty += qty

            line['uq'] = convert_unit(order_line.product_uom.name)
            line['dateLiv'] = order_line.date_planned.strftime('%Y%m%d')
            line['uep'] = 1    # CHECKME

            lines.append(line)

        # 300
        record['totalQte'] = totalQty
        record['totalLigne'] = line_index+1
        record['totalHT'] = int(order.amount_untaxed * 1000)
        record['totalTVA'] = int(order.amount_tax * 1000)
        record['totalTTC'] = int(order.amount_total * 1000)
        #    for order in po.browse(po_ids):
        #        print order.name
        #        for ol in order.order_line:
        #            print ol
        #        return order
        record['__lines__'] = lines
        return record


def htmldoc(doc):
    spec = doc.content[2]
    print '<html><head>'
    print '<meta charset="UTF-8"></meta>'
    print '<title>Spec</title></head><body>'
    headers = ('name', 'required', 'type_', 'size', 'offset', 'value')
    for section in spec.sections:
        # print "\nPROCESSING", section
        print '<h1>', section.index, section.title, '</h1>'
        rec = list(section.convert_to_objects())
        print '<table>'
        print "<tr>"
        for h in headers:
            print "<th>%s</th>" % h
        print "</tr>"
        for field in rec:
            print '<tr>'
            for k in headers:
                if k == 'name':
                    print '<td>', getattr(field, k), '</td>'
                else:
                    print '<td>', getattr(field, k), '</td>'
            print '</tr>'
        print '</table>'
    print '</body></html>'


def main():
    from optparse import OptionParser
    parser = OptionParser()
    option = parser.add_option
    option('-d', "--debug", dest="debug", action="store_true")
    option('-D', "--docgen", dest="docgen", action="store_true")
    option('-j', "--json-read", dest="jsonread", action="store_true")
    option('-J', "--json-write", dest="jsonwrite", action="store_true")
    option('-M', "--mustache", dest="mustache", action="store_true")
    option('-s', "--save", dest="save", action="store_true")
    option('-i', "--edi-read", dest="ediread", action="store_true")
    option('-I', "--edi-write", dest="ediwrite", action="store_true")
    option('-r', "--rpc", dest="rpc", action="store_true")
    logging.basicConfig()
    (options, args) = parser.parse_args()

    if options.debug:
        import edifact
        edifact.DEBUG = True
        _logger.setLevel(logging.DEBUG)

    doc = Debonix()
    doc.build_templates()

    if options.docgen:
        htmldoc(doc)

    if options.mustache:
        with open("debonix.mustache", "w") as out:
            out.write(doc.template)

    if options.save:
        with open("debonix.json", "w") as out:
            out.write(simplejson.dumps(doc.tojson(), sort_keys=True, indent=4 * ' '))

    for ref in args:
        if options.rpc:
            record = rpc_read_edifact(ref)
        elif options.ediread:
            raise NotImplementedError, "reading edifact"
        elif options.jsonread:
            with open("%s.json" % ref) as data:
                record = simplejson.load(data)
        if options.ediwrite:
            with open('%s.edi' % ref, 'w') as out:
                out.write(doc.render(record).encode('latin1'))
        if options.jsonwrite:
            with open('%s.json' % ref, 'w') as out:
                out.write(simplejson.dumps(record))


    # generate_edifact(ref)

if __name__ == "__main__":
    main()
