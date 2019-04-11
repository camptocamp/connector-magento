# Quality checks on pull requests

## Performed checks

You can put a **#trivial** marker in a pull request body to mark it as something
simple and straightforward.

### Warnings (won't cause the build to fail)

- PR headline contains **[WIP]** marker
- PR has a **work in progress** label on it
- Large diff (500+ lines)
- `HISTORY.rst` hasn't changed in a pull request (unless your PR is "trivial")
- you've made changes to a `.py` files in a local module, but didn't stated it
  in a last migration step `odoo/migration.yml`
- `.py` files were changed, but not tests *(pretty much naive)*
- last migration version in `migration.yml` targets released version and upgrade
  is advised (`.py` files were updated in a module that is absent in a last
  migration step - this is a warning since it's not a mandatory to upgrade a
  module after any `.py` update)

### Errors (would cause the build to fail)

- you've made changes to a `.xml` files in a local module, but didn't stated it
  in a last migration step `odoo/migration.yml` - behaves pretty much like the
  previous check, but generates an error instead.
- last migration version in `migration.yml` targets released version and upgrade
  is required (`.xml` files were updated in a module that is absent in a last
  migration step)

Commit message is undergoing a "lint check" as well as the diff:
- message has to consist of more than a single word
- message has to start from a Capital Letter
- message shouldn't have a period at the end
- headline has to be separated from the body with a blank line

### Roadmap

- [ ] Handle mismatched remotes on submodules with pending merges

  Currently, Dangerfile features a fancy check for mismatched remotes in a
  submodules with pending merges in 'em in order to be able to see which of
  those an author should alter w/o having to dig into Travis build logs
  (possibly multiple times, since Travis reveals one broken remote at a time).
  Though, I've never had a chance to actually observe the outcome on a live PR,
  since current submodule remote check is executed slightly before Danger is
  meant to be run and, as was stated before, is quite paranoid and fails badly
  in the case that Danger should handle as well - so we'll need to teach those
  guys how to play well w/ each other.

- [ ] Enhance `migration.yml` check for `.py` files

  I.e., it's safe to say that if `.py` diff contains something like
  ```diff
  - something = fields.Type(whatever)
  + something = fields.Type(altered whatever)
  ```
  then a module that holds a modified file should be present in a last migration.
  Currently, a facilities to get a last migration step's upgrade lists and/or
  extracting module name from a modified file name have been implemented (though
  it might be better to have them extracted to functions)

- [ ] Teach last migration step getter to feel itself comfortable in various `migration.yml` structures

  Currently, it's designed to work in a structure similar to this:
  ```yaml
  migration:
    versions:
      v1:
        addons:
          - ...
      v1:
        addons:
          - ...
  ```
  Imagine having different upgrade lists for different Marabunta modes, like:
  ```yaml
  migration:
    versions:
      v1:
        modes:
          full:
            addons:
              - ...
          sample:
            addons:
              - ...
  ```
  and so on. It'll work in most cases, but won't be able to get through
  additional `modes/<mode>` wraps at the moment.
  Preventive countermeasures were made, so Danger should operate more or less
  fine, except for `migration.yml` check itself in such cases.

- [ ] Track changes in updated submodules

  We can bug people to upgrade previously installed modules with changes in the
  upstream.

- [ ] Ensure that every module mentioned in migration steps is present in `setup` step
