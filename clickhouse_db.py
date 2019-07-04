#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Gustavo Campos <guhcampos@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
import time
from ansible.module_utils.basic import AnsibleModule
from clickhouse_driver import Client as ClickhouseClient

CLICKHOUSE_DEFAULT_PORT = 9000
CLICKHOUSE_DEFAULT_HOST = 'localhost'
POLLING_ATTEMPTS = 10
POLLING_INTERVAL = 1
SUPPORTED_STATES = ['present', 'absent']


def db_exists(client_params, db):
    client = ClickhouseClient(**client_params)

    databases = client.execute('SHOW DATABASES')

    if db in [database[0] for database in databases]:
        return True
    return False


def db_create(client_params, db):
    """
    Create a database on the currently logged in host.
    """
    client = ClickhouseClient(**client_params)
    if not db_exists(client_params, db):
        client.execute('CREATE DATABASE {db}'.format(db=db))

        # wait until database is created
        for _ in range(POLLING_ATTEMPTS):
            if db_exists(client_params, db):
                break
            time.sleep(POLLING_INTERVAL)
        return True

    return False


def db_delete(client_params, db):
    """
    Delete a database on the currently logged in host.
    """
    client = ClickhouseClient(**client_params)
    if db_exists(client_params, db):
        client.execute('DROP DATABASE {db}'.format(db=db))
        # wait until database is deleted
        for _ in range(POLLING_ATTEMPTS):
            if not db_exists(client_params, db):
                break
            time.sleep(POLLING_INTERVAL)

        return True
    return False


def main():

    result = dict(changed=False, msg='')

    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=SUPPORTED_STATES),
        user=dict(type='str'),
        password=dict(type='str', no_log=True),
        host=dict(type='str', default=CLICKHOUSE_DEFAULT_HOST),
        port=dict(type='int', default=CLICKHOUSE_DEFAULT_PORT),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    client_params = dict()
    client_params['host'] = module.params['host']
    client_params['port'] = module.params['port']

    if module.params['user']:
        client_params['user'] = module.params.get['user']

    if module.params['password']:
        client_params['password'] = module.params.get['password']

    if module.params['state'] == 'present':
        result['changed'] = db_create(client_params, module.params['name'])

    elif module.params['state'] == 'absent':
        result['changed'] = db_delete(client_params, module.params['name'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
