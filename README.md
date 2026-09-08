### Erpnext To Erpnext Havano

ERPNext communication with another ERPNext server.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app erpnext_to_erpnext_havano
bench migrate
```

### Usage

**All steps detailed below are to be done on the server acting as the local unless otherwise stated**

To use this app, you will install it on both erpnext server you want to communicate with and both sites should have been setup the same way to avoid error(same companies on site setup) a fresh site is recommended.

Before its usage make sure the app acting as a cloud (the one that sends record and receives sale invoices) can be accessed with using api key for administrator access. If it hasnt yet been allowed please do so and add the generated keys in a .env file for both the cloud and local in the root of this repo with the api kay and secret as shown below:

```
API_KEY="add_the_api_key"
API_SECRET="add_the_secret"
```

After installation, go the **ERPNext to ERPNext Sync Settings** doctype for the server that will be receiving records and send out the invoices and set that as the local by checking the **"Is Local"** checkbox. Leave the checkbox unchecked for the server acting as the cloud. Then set your cloud url and the local url.

Create an email group that will serve as the system administrators to be notified when any error occurs and add members to the emails then in the **ERPNext to ERPNext Sync Settings** doctype update the email group name field.

Now after all these have been done migrate your site so the syncing can be done every 2 minutes. You can edit the frequency from the scheduler_events in hooks.py

```
bench --site site-name migrate
bench --site site_name enable-scheduler
```

Use to check if the scheduler is active then restart your bench
```
bench --site site_name scheduler status
```

The syncing will automatically take place every 5 minutes and incase of any errors the members of the email group will be notified and error logs.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/erpnext_to_erpnext_havano
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit
