# -*- mode: ruby -*-
# Sometimes it's a README fix, or something like that - which isn't relevant for
# including in a project's HISTORY.rst for example
declared_trivial = (github.pr_title + github.pr_body).include? "#trivial"
impacted_files = git.modified_files | git.added_files | git.deleted_files
modified_python_files = impacted_files.select{ |i| i[/local-src\/.*\.py$/] }
modified_xml_files = impacted_files.select{ |i| i[/local-src\/.*\.xml$/] }
has_local_python_changes = !modified_python_files.empty?
has_tests_changes = !git.modified_files.grep(/tests/).empty?

# Mainly to encourage writing up some reasoning about the PR, rather than
# just leaving a title
if github.pr_body.length < 5
  fail "Please provide a summary in the Pull Request description"
end

# Make it more obvious that a PR is a work in progress and shouldn't be merged yet
warn("PR is headlined as Work in Progress") if github.pr_title.include? "[WIP]"
warn("PR has a 'work in progress' label on it") if github.pr_labels.include? "work in progress"

# Warn when there is a big PR
warn("Big PR") if git.lines_of_code > 500

# we could consider using danger-changelog but then probably switch history to markdown
no_changelog_entry = !git.modified_files.include?("HISTORY.rst")
if no_changelog_entry && !declared_trivial
  warn("Please consider adding a note in HISTORY.rst")
end

### migration.yml checks
require("yaml")
migration_file = File.read("odoo/migration.yml")
# Hash.dig("a", "b") is a safer version of Hash["a"]["b"]
version_migrations = YAML.load(migration_file).dig("migration", "versions")
latest_version_migration = version_migrations[-1] if version_migrations
addons_to_upgrade = latest_version_migration.dig("addons", "upgrade")

# TODO: currently, it's impossible to get an addons_to_upgrade list in the case when
# it is hidden under `modes` section or something similar - it works only in
# cases when `addons` section is a direct ancestor of an element of `versions` array
unless addons_to_upgrade
  warn("Skipping migration.yml check cause of incompatible .yml structure" \
       " - please revise your last migration step yourself")
else
  # ensure that each module is listed only once in the last migration step
  # array.uniq! would return `nil` if that array held unique values at the moment of calling
  warn("Last migration step contains duplicates") if addons_to_upgrade.uniq!

  # check if migration.yml is intact w/ the latest changes
  # Hard check: modules having XML updates - update is *required*
  # `split` following the common pattern "odoo/local-src/<module_name>/..."
  # to get the module name out of it
  xml_impact_modules = modified_xml_files.map{ |i| i.split("/")[2] }.uniq
  # names of modules present in diff, though absent in an last upgrade step
  upgrade_required = xml_impact_modules - addons_to_upgrade
  # fail w/ informative msg if not every impacted module is present in the last migration step
  unless upgrade_required.empty?
    migration_needed_msg = ".xml: entry in a last migration.yml is required for modules: "
    migration_needed_msg += upgrade_required.join(", ")
    migration_needed_msg += " // please state every local module in a migration.yml explicitly"
    fail(migration_needed_msg)
  end

  # Soft check: modules having Python updates - update is advised
  python_impact_modules = modified_python_files.map{ |i| i.split("/")[2] }.uniq
  upgrade_advised = python_impact_modules - addons_to_upgrade
  # since we're done w/ `upgrade required` step now,
  # we don't need to highlight those for the second time
  upgrade_advised -= upgrade_required
  unless upgrade_advised.empty?
    migration_advised_msg = ".py: entry in a last migration.yml is advised for modules: "
    migration_advised_msg += upgrade_advised.join(", ")
    migration_advised_msg += " // please state every local module in a migration.yml explicitly"
    warn(migration_advised_msg)
  end
end

# check if requested migration step targets the correct version
latest_released_version = File.read("odoo/VERSION").split("\n")[0]
if latest_version_migration["version"] <= latest_released_version
  invalid_target_version_msg = "Last migration step targets already released version."
  if upgrade_required
    # then we surely need to do a next migration step
    fail(invalid_target_version_msg)
  else
    # still it is possible that no upgrades were required since last release
    warn(invalid_target_version_msg)
  end
end

if has_local_python_changes && !has_tests_changes
  warn("There are changes in local addons but no new test. Please consider adding some.", sticky: false)
end

### Submodule sanity check
# FIXME: currently is being shadowed by the original one
# https://github.com/camptocamp/odoo-template/blob/ee96d4b/%7B%7Bcookiecutter.repo_name%7D%7D/travis/git_submodule_update.py#L49
require('git')
repo = Git.open(".")
# actual submodule paths (hashtable a.k.a. dict)
submodules = repo.config.select{ |k, v| k[/^submodule\.odoo\/[\w\/-]+/] }
pending_merges = (YAML.load(File.open("odoo/pending-merges.yaml")) or {})

def normalize_git_url(url)
  url.downcase!
  url.sub!("git@github.com:", "https://github.com/") if url.match(/git@github\.com:/)
  url = url[0..-5] if url.match(/.*\.git$/)
end

# pattern: |submodule.odoo/<path>.url| => <remote URL>
#          |0 --------- 14 ^--- ^ -5 |
for submodule_path, target_url in submodules
  submodule_path = "." + submodule_path[14..-5]
  if pending_merges.key?(submodule_path)
    pending_repo = pending_merges[submodule_path]
    target = pending_repo["target"].split()[0]
    target_remote = pending_repo["remotes"][target]
    if normalize_git_url(target_remote) != normalize_git_url(target_url)
      fail(%{
In .gitmodules #{submodule_path}:
   remote #{target_remote} does not match
   target url #{target_url}
   in pending.merges.yml
   })
    end
  end
end

commit_lint.check disable: [:subject_length, :subject_cap]
