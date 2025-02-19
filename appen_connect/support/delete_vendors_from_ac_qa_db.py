import sshtunnel
import mysql.connector
import os

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

find_all_tables_with_column = """
SELECT DISTINCT TABLE_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE COLUMN_NAME IN ('user_id')
        AND TABLE_SCHEMA='qrp' and TABLE_NAME like 'user%' and TABLE_NAME not like 'user_payoneer_ids';
"""

find_user_id = 'select id from qrp.users where email = %s;'


def find_vendors(search_mode, vendors, cnx):
    cursor = cnx.cursor()

    vendors_exist = []
    vendors_not_found = []

    for search_value in vendors:
        # find user id
        if search_mode == 'email':
            cursor.execute("select id from qrp.users where email = '%s';" % search_value)
            _user = cursor.fetchall()
            if _user:
                vendors_exist.append(search_value)
            else:
                vendors_not_found.append(search_value)

    return vendors_exist, vendors_not_found


def delete_vendors_by(search_mode, vendors, cnx):
    cursor = cnx.cursor()

    cursor.execute(find_all_tables_with_column)
    tables = [i[0] for i in cursor.fetchall()]
    tables.append('exp_user_groups')
    tables.append('exp_user_locales')

    for search_value in vendors:
        print("Vendor: ", search_value)
        # find user id
        if search_mode == 'email':
            cursor.execute("select id from qrp.users where email = '%s';" % search_value)
            _user = cursor.fetchall()
            if _user:
                user_id = _user[0][0]
            else:
                print(" --- vendor %s has not been found" % search_value)
                continue
        else:
            user_id = search_value

        for t in tables:
            check_records = 'select * from qrp.%s where user_id = %s limit 10;' % (t, user_id)
            cursor.execute(check_records)
            logs = cursor.fetchall()
            if len(logs) > 0:
                print("-=-=-TABLE -=-==-", t)
                print(logs)
                # cursor.execute('SET SQL_SAFE_UPDATES = 0;')
                delete_records = "delete from qrp.%s where user_id = '%s'; " % (t, user_id)
                cursor.execute(delete_records)
                cnx.commit()

        delete_records = "delete from qrp.users where id = '%s'; " % user_id
        print("users SQL: ", delete_records)
        cursor.execute(delete_records)
        cnx.commit()
        print(' ---  vendor %s has been deleted' % search_value)


if __name__ == '__main__':
    mode = input("Do you want to search vendors by email? (yes/no):")
    vendors = input('Please provide list of vendors (exp, test@gmail.com;test2@gmail.com): ')
    search_mode = 'email' if mode else 'id'

    vendors = [x.strip() for x in vendors.split(";")]

    DB_ADDRESS_QA = os.getenv('DB_ADDRESS_QA')
    if not DB_ADDRESS_QA:
        print("DB_ADDRESS_QA has not been found")
        DB_ADDRESS_QA = input("Please, provide DB Address:")

    DB_USER_QA = os.getenv('DB_USER_QA')
    if not DB_USER_QA:
        print("DB_USER_QA has not been found")
        DB_USER_QA = input("Please, provide DB admin username:")

    DB_PASSWORD_QA = os.getenv('DB_PASSWORD_QA')
    if not DB_PASSWORD_QA:
        print("DB_PASSWORD_QA has not been found")
        DB_PASSWORD_QA = input("Please, provide DB admin password:")

    SSH_KEY = os.getenv('SSH_KEY')
    if not SSH_KEY:
        print("SSH_KEY has not been found")
        SSH_KEY = input("Please, provide path to SSH KEY:")

    with sshtunnel.SSHTunnelForwarder(ssh_address_or_host='ec2-34-215-59-58.us-west-2.compute.amazonaws.com',
                                      ssh_username="ec2-user",
                                      ssh_pkey=SSH_KEY,
                                      remote_bind_address=(DB_ADDRESS_QA, 3306),
                                      ) as tunnel:
        cnx = mysql.connector.MySQLConnection(user=DB_USER_QA,
                                              password=DB_PASSWORD_QA,
                                              host='127.0.0.1',
                                              database='qrp',
                                              port=tunnel.local_bind_port,
                                              use_pure=True)

        if cnx.is_connected():
            db_Info = cnx.get_server_info()
            print("Connected to MySQL Server version ", db_Info)

            vendors_exist, vendors_not_found = find_vendors(search_mode=search_mode, vendors=vendors, cnx=cnx)

            if vendors_not_found:
                print("!!! Accounts have not been found:", ';'.join(vendors_not_found))

            if vendors_exist:
                _vendors = ';'.join(vendors_exist)
                del_account = input("Accounts have been found: \n %s \nDo you want to delete accounts: (yes/no)" % _vendors)
                if del_account == 'yes':
                    print("-- "+_vendors + " will be deleted")
                    delete_vendors_by(search_mode=search_mode, vendors=vendors_exist, cnx=cnx)
                else:
                    print("No accounts to delete")
        cnx.close()

    print("Done!!!")

"""
1.to use this script you need following python libraries: sshtunnel, mysql-connector-python
install it if you don't have it already:

pip install sshtunnel mysql-connector-python


2. recommended to store sensitive (db credentials) information in env variables. 
if you don't store these params as env variables, script will ask you to provide this params, eg. 
""
DB_ADDRESS_QA has not been found
Please, provide DB Address:
""

SSH_KEY - path to the public key for ssh access (file with pem extension) , eg. /Users/<username>/.ssh/lf_vpc_aws_kp_20180308_stage.pem'

export DB_ADDRESS_QA=<>
export DB_USER_QA=<>
export DB_PASSWORD_QA=<>
export SSH_KEY=<>


3. run script

python delete_vendors_from_ac_qa_db.py


4. script parameters:

 --- Do you want to search vendors by email? (yes/no): yes - if you provide list of vendors email
                                                       no  - if you provide list of vendors ids
                                                       
 --- Please provide list of vendors (exp, test@gmail.com;test2@gmail.com): --- list of ids or emails, use ; as separator
                                                                           e.g -  SignUPQA002connect.stage.xyz@gmail.com; SignUPQA003connect.stage.xyz@gmail.com;SignUPQA004connect.stage.xyz@gmail.com;SignUPQA005connect.stage.xyz@gmail.com
                                                                               - 129164;129189;129938
                                                                               
"""
