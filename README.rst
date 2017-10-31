=================
Passed Smoke Test
=================



.. image:: https://pyup.io/repos/github/barleyj-puppet/passed_smoke_test/shield.svg
     :target: https://pyup.io/repos/github/barleyj-puppet/passed_smoke_test/
     :alt: Updates


Python utility that checks to see if a commit has made it through smoke testing.


Insallation
--------
* Clone the repo.::

      git clone git@github.com:barleyj-puppet/passed_smoke_test.git

* Set your Jenkins username and api token up. The token can be found by clicking your name and selecting configure then clicking the "Show API Token" button.::

      export JENKINS_USERNAME='your.username'
      export JENKINS_TOKEN='your api token'

* Set your Jira username and api token up.::

      export JIRA_USERNAME='your.username'
      export JIRA_TOKEN='your api token'

* Set your Github username and api token up.::

      export GITHUB_USERNAME='your.username'
      export GITHUB_TOKEN='your api token'

* Jira, Jenkins, and Github tokens will be securely prompted for if they are not set in an environment variable or passed in as an option.

* Install passed_smoke_test. From within the passed_smoke_test directory run.::

      python setup.py install

      # If you are doing development, this will symlink the source directory
      python setup.py develop


Features
--------
* Check if the latest repo commit was tested in the lastest smoke test.::

      passed_smoke_test latest_build --repo puppetlabs-pe_repo --branch davis

* Check what commits are in the latest enterprise-dist.::

      passed_smoke_test commits --repo puppetlabs-pe_repo --branch glisan
      commit 98130963dcf3be0d45c0f9765aad0e93b1c0f0e0

        Merge pull request #337 from puppetlabs/mergeup/2016.4.x_to_glisan/2017_09_11_17_58

        Mergeup/2016.4.x to glisan/2017 09 11 17 58

      commit 7312bd23cb4f28fd0f36b2cee1017be43b8072ec

        Merge pull request #335 from ajroetker/PE-22243

        (PE-22243) Add hiera.yaml to configure module to pull data from pe.conf

      commit c79a203482759d82ca3759cadb776ba44f5d5993

        Merge pull request #333 from puppetlabs/mergeup/2016.4.x_to_glisan/2017_09_06_22_41

        Mergeup/2016.4.x to glisan/2017 09 06 22 41

      commit 2f26cddd39c3a81e574dbc4676e87e42cef6bc38

        Merge pull request #330 from puppetlabs/mergeup/2016.4.x_to_glisan/2017_09_01_22_43

        Mergeup/2016.4.x to glisan/2017 09 01 22 43

* Check what the last commit of a repo was if it passed one of the current smoke tests::

      passed_smoke_test last_build --repo puppetlabs-pe_manager --branch hoyt
      Commit 31815ef244ea7fdf9a49689c28d5f611fb45977c in repo puppetlabs-pe_manager passed smoke test in build 2017.3.2-rc1-58-ge8209b5


* Check if all branch commits for a ticket have passed smoke test and been promoted::

      passed_smoke_test ticket --branch hoyt --ticket PE-22678 --jira-username jayson.barley
      Ticket PE-22678 passed smoke test in build 2017.3.2-rc1-37-gf90291d
      Ticket PE-22678 was promoted in build 2017.3.2-rc1-37-gf90291d

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
