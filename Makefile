# Update this list when you add a new test.
TESTS = \
    course_discovery \
    course_import \
    credentials \
    csm \
    discussions_api \
    ecommerce \
    enrollment \
    lms \
    teams_discussion

help:
	@echo 'see README.rst for usage details'

requirements:
	pip install -r requirements.txt --exists-action w

# I don't understand why the .SECONDEXPANSION feature needs to be enabled to
# use $@ (target reference) in prerequisites, but it does.  Please help to
# figure out a cleaner solution.
.SECONDEXPANSION:

# If the settings file is missing, just copy the example settings.  If the
# settings file already exists, this recipe will not be triggered. Your custom
# settings should never not be overwritten.
settings_files/%.yml: $$@.example
	cp $< $@

$(TESTS): settings_files/$$@.yml
	locust --host=$(HOST) -f $@

.PHONY: help requirements $(TESTS)
.DEFAULT: help
