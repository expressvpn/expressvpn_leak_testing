.PHONY: lint
lint:
	git lint

.PHONY: lint-all
lint-all:
	. activate && find . -iname "*.py" -a -not -path "./no_git/*" | xargs pylint

.PHONY: lint-install
lint-install:
	. activate && pip install pylint && pip install git-lint

.PHONY: test
test:
	. activate && python -m unittest discover -v

# TODO: None of the setup really works well or is cross platform
setup: setup_homebrew setup_python

setup_homebrew:
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" && \
	brew install python

setup_python: ./setup_python.sh ~/xv_leak_testing_python
