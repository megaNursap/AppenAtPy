import psycopg2
import psycopg2.extras


# the wait_select callback can handle a KeyboardInterrupt (Ctrl-C) correctly.
psycopg2.extensions.set_wait_callback(psycopg2.extras.wait_select)
