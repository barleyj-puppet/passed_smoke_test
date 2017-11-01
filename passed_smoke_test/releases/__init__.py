from collections import defaultdict


def defaults():
    return {
        'davis': '2016.4.x',
        'glisan': '2017.2.x',
        'hoyt': '2017.3.x',
        'irving': '2018.1.x',
    }


releases = defaultdict(defaults)

exceptions = {
    'puppetlabs-pe_repo': {
        'davis': '2016.4.x',
        'glisan': 'glisan',
        'hoyt': 'hoyt',
        'irving': 'irving',
    },
    'puppetlabs-pe_manager': {
        'davis': 'davis',
        'glisan': 'glisan',
        'hoyt': 'hoyt',
        'irving': 'irving',
    },
    'puppetlabs-puppet_enterprise': {
        'davis': '2016.4.x',
        'glisan': 'glisan',
        'hoyt': 'hoyt',
        'irving': 'irving',
    },
    'puppetlabs-pe_infrastructure': {
        'davis': '2016.4.x',
        'glisan': 'glisan',
        'hoyt': 'hoyt',
        'irving': 'irving',
    }

}

releases.update(exceptions)
