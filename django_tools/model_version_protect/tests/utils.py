def shorten_logs(logs):
    return [
        log.replace(':django_tools.model_version_protect.models:', ': ')
        for log in logs
    ]
