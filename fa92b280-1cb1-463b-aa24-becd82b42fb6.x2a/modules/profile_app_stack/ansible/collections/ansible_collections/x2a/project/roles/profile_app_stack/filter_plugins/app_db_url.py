from urllib.parse import quote

from ansible.errors import AnsibleFilterError


def app_db_url(user, password, host, port, database):
    """Build a PostgreSQL URL with safely escaped user and password."""
    try:
        escaped_user = quote(str(user), safe="")
        escaped_password = quote(str(password), safe="")
        escaped_host = str(host)
        escaped_database = quote(str(database), safe="")
        return f"postgresql://{escaped_user}:{escaped_password}@{escaped_host}:{int(port)}/{escaped_database}"
    except (TypeError, ValueError) as exc:
        raise AnsibleFilterError(f"Unable to construct database URL: {exc}") from exc


class FilterModule:
    def filters(self):
        return {"app_db_url": app_db_url}
