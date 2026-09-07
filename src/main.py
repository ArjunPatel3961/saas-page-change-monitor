import argparse

from monitor_service import Tenant, inspect_tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Check one SaaS page and print a change alert")
    parser.add_argument("url")
    parser.add_argument("--tenant", default="demo-tenant")
    parser.add_argument("--previous-digest")
    args = parser.parse_args()
    tenant = Tenant(args.tenant, args.url, "admin@example.com")
    alert = inspect_tenant(tenant, args.previous_digest)
    if alert:
        print(f"CHANGE tenant={alert.tenant_id} url={alert.page_url} digest={alert.current_digest}")
    else:
        print(f"UNCHANGED tenant={tenant.tenant_id} url={tenant.page_url}")


if __name__ == "__main__":
    main()

