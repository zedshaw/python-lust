from ConfigParser import SafeConfigParser


def load_ini_file(file_name, defaults={}):
    config = SafeConfigParser()
    config.readfp(open(file_name))
    results = {}

    for section in config.sections():
        for key, value in config.items(section):
            results[section + '.' + key] = value

    results.update(defaults)

    return results

