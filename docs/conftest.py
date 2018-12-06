def pytest_collectstart(collector):
    collector.skip_compare += ('text/plain', 'application/vnd.jupyter.widget-view+json',)