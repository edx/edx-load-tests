# This makefile primarily abstracts the installation of dependencies and
# settings files, which is helpful for loadtest automation scripts.  

# determine the filename suffix used to find the correct settings file
# template.
EXAMPLE_SUFFIX = .example
ifdef LT_ENV
    ifneq (,$(LT_ENV))
        EXAMPLE_SUFFIX = .$(LT_ENV)-example
    endif
endif

# figure out what all the loadtests are
LOADTESTS := $(wildcard loadtests/*)  # get all files in the loadtests dir
LOADTESTS := $(LOADTESTS:loadtests/%=%)  # get the loadtest name only
LOADTESTS := $(filter-out __init__.py,$(LOADTESTS))  # filter out the __init__.py file

# create another list with "-requirements" suffixed to the loadtest names
LOADTEST_REQUIREMENTS := $(LOADTESTS:%=%-requirements)

help :
	@echo 'Make Targets:'
	@echo '    <testname>: Install everything needed for running the <testname> loadtest.'
	@echo '    <testname>-requirements:'
	@echo '         Install only the pip requirements for running the <testname> loadtest.'
	@echo '    requirements: Install development pip requirements.'
	@echo '    util-requirements: Install data analysis pip requirements only.'
	@echo ''
	@echo 'Environment Variables:'
	@echo '    LT_ENV:'
	@echo '        Optionally specify the name of the target loadtest environment (e.g.'
	@echo '        devstack, sandbox). If this varaible is absent, the default environment'
	@echo '        is selected and is guaranteed to have a settings file present.'
	@echo ''
	@echo 'Usage Examples:'
	@echo '    `make lms`: Prepare to run the lms load test using the standard settings.'
	@echo '    `LT_ENV=sandbox make lms`:'
	@echo '        Prepare to run the lms load test against a sandbox, given that the'
	@echo '        sandbox-specific settings are present under'
	@echo '        settings_files/lms.sandbox-example.'

requirements :
	@echo 'NOTE: installing minimal pip requirements needed for development'
	pip install -r requirements.txt --exists-action w

util-requirements :
	@echo 'NOTE: installing pip requirements needed for data analysis'
	pip install -r util/util_requirements.txt --exists-action w

# install pip requirements for a specific loadtest, e.g. make lms-requirements
# Note: the automatic variable `$*` represents the loadtest name
$(LOADTEST_REQUIREMENTS) : %-requirements :
	@echo 'NOTE: installing pip requirements needed for running the $* loadtest'
	pip install -r loadtests/$*/requirements.txt --exists-action w

# Install a settings file from a template.  If the settings file is missing
# then just copy the example settings, but your WIP settings should never be
# overwritten.
#
# Note: The automatic variable `$*` represents the loadtest name, and the pipe
#       symbol `|` enforces that existing settings files do not get overwritten
#       because the example template got updated.  Thus, we use the `$|` symbol
#       to refer to the settings example template.
settings_files/%.yml : | settings_files/%.yml$(EXAMPLE_SUFFIX)
	@echo 'NOTE: installing $* settings from a template'
	cp $| $@

# This rule should be the only one that is required to run directly by users
# and automation scripts, e.g. `make lms`.  It does not invoke locust because
# there's no way to know which command line options are needed by the user, so
# it would not be generally useful.
$(LOADTESTS) : % : %-requirements settings_files/%.yml
	@echo ""
	@echo "HINT: Configure the $@ load test using the file:"
	@echo "    settings_files/$@.yml"
	@echo "HINT: Run the $@ load test with:"
	@echo "    locust --host=<HOST> -f loadtests/$@"

.PHONY: help requirements util-requirements $(LOADTESTS) $(LOADTEST_REQUIREMENTS)
.DEFAULT: help
