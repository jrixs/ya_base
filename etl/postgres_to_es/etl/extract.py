import os
from datetime import datetime

from dotenv import load_dotenv
from etl.connect import tryfetchmany, log
from etl.statistics import etl_settings
from etl.transform import transform_filmwork
from psycopg2.extras import DictCursor, RealDictCursor
from etl import sql

load_dotenv()

max_line = int(os.environ.get('DB_PORT', 50))

date_format = '%Y.%m.%d %H:%M:%S.%f'
datetime_min = f"000{datetime.min.strftime(date_format)}"


def сheck_filmwork(conn) -> list:
    start_time = etl_settings.get_state('START_TIME_FILMWORK')
    start_time = start_time if start_time else datetime_min
    set_uuids: list = []

    def get_filmwork(uuids: list):
        r_uuids = [dict(row) for row_list in uuids for row in row_list]
        if not r_uuids:
            log.info("FILMWORK Новых записей или обновлений не найнодо.")
            return

        log.info("FILMWORK Есть данные для добавления.")
        uuid_list = [_.get('id') for _ in r_uuids]
        uuid_list = "'{0}'".format('\',\''.join(uuid_list))
        max_modified = max([_.get('modified') for _ in r_uuids]) \
            if len(r_uuids) > 1 else r_uuids[0]['modified']

        result = transform_filmwork(
                    tryfetchmany(
                        pg_conn=conn.cursor(cursor_factory=DictCursor),
                        lines=max_line,
                        sqlreq=sql.FILMWORK_DATA.format(uuid_list)
                    )
                )

        if result:
            for line in r_uuids:
                log.info(f"ADDED OR UPDATE {line.get('id')}")
                set_uuids.append(line.get('id'))
            date_start_time = datetime.strptime(start_time, date_format)
            timezone = max_modified.tzinfo
            date_start_time = date_start_time.replace(tzinfo=timezone)
            if max_modified > date_start_time:
                etl_settings.set_state('START_TIME_FILMWORK',
                                       max_modified.strftime(date_format))

    get_filmwork(
        tryfetchmany(
            pg_conn=conn.cursor(cursor_factory=RealDictCursor),
            lines=max_line,
            sqlreq=sql.FILMWORK_MODIFIED.format(start_time)
        )
    )

    return set_uuids


def сheck_person(conn, set_uuid) -> list:
    start_time = etl_settings.get_state('START_TIME_PERSON')
    start_time = start_time if start_time else datetime_min
    set_uuids: list = []

    def send_filmwork(uuids: list):
        r_uuids = [dict(row) for row_list in uuids for row in row_list]
        uuid_list = [_.get('id') for _ in r_uuids
                     if _.get('id') not in set_uuid]
        if not uuid_list:
            return True

        uuid_list = "'{0}'".format('\',\''.join(uuid_list))

        result = transform_filmwork(
                    tryfetchmany(
                        pg_conn=conn.cursor(cursor_factory=DictCursor),
                        lines=max_line,
                        sqlreq=sql.FILMWORK_DATA.format(uuid_list)
                    )
                )

        if result:
            for line in r_uuids:
                log.info(f"ADDED OR UPDATE {line.get('id')}")
                set_uuids.append(line.get('id'))

        return result

    def get_filmwork_id(person_id: list):
        person_id = [dict(__) for _ in person_id for __ in _]
        if not person_id:
            log.info("PERSON Новых записей или обновлений не найнодо")
            return

        log.info("PERSON Есть данные для добавления.")
        uuid_list = [_.get('id') for _ in person_id]
        uuid_list = "'{0}'".format('\',\''.join(uuid_list))
        max_modified = max([_.get('modified') for _ in person_id]) \
            if len(person_id) > 1 else person_id[0]['modified']

        result = send_filmwork(
            tryfetchmany(
                pg_conn=conn.cursor(cursor_factory=RealDictCursor),
                lines=max_line,
                sqlreq=sql.PERSON_GET_FILMWORK_ID.format(uuid_list)
            )
        )

        if result:
            date_start_time = datetime.strptime(start_time, date_format)
            timezone = max_modified.tzinfo
            date_start_time = date_start_time.replace(tzinfo=timezone)
            if max_modified > date_start_time:
                etl_settings.set_state('START_TIME_PERSON',
                                       max_modified.strftime(date_format))

    get_filmwork_id(
        tryfetchmany(
            pg_conn=conn.cursor(cursor_factory=RealDictCursor),
            lines=max_line,
            sqlreq=sql.PERSON_ID_MODIFIED.format(start_time)
        )
    )

    return set_uuids + set_uuid


def сheck_genre(conn, set_uuid) -> list:
    start_time = etl_settings.get_state('START_TIME_GENRE')
    start_time = start_time if start_time else datetime_min
    set_uuids: list = []

    def send_filmwork(uuids: list):
        r_uuids = [dict(row) for row_list in uuids for row in row_list]
        uuid_list = [_.get('id') for _ in r_uuids
                     if _.get('id') not in set_uuid]

        if not uuid_list:
            return True

        uuid_list = "'{0}'".format('\',\''.join(uuid_list))

        result = transform_filmwork(
                    tryfetchmany(
                        pg_conn=conn.cursor(cursor_factory=DictCursor),
                        lines=max_line,
                        sqlreq=sql.FILMWORK_DATA.format(uuid_list)
                    )
                )

        if result:
            for line in r_uuids:
                log.info(f"ADDED OR UPDATE {line.get('id')}")
                set_uuids.append(line.get('id'))

        return result

    def get_filmwork_id(person_id: list):
        person_id = [dict(__) for _ in person_id for __ in _]
        if not person_id:
            log.info("GENRE Новых записей или обновлений не найнодо")
            return

        log.info("GENRE Есть данные для добавления.")
        uuid_list = [_.get('id') for _ in person_id]
        uuid_list = "'{0}'".format('\',\''.join(uuid_list))
        max_modified = max([_.get('modified') for _ in person_id]) \
            if len(person_id) > 1 else person_id[0]['modified']

        result = send_filmwork(
            tryfetchmany(
                pg_conn=conn.cursor(cursor_factory=RealDictCursor),
                lines=max_line,
                sqlreq=sql.GENRE_GET_FILMWORK_ID.format(uuid_list)
            )
        )

        if result:
            date_start_time = datetime.strptime(start_time, date_format)
            timezone = max_modified.tzinfo
            date_start_time = date_start_time.replace(tzinfo=timezone)
            if max_modified > date_start_time:
                etl_settings.set_state('START_TIME_GENRE',
                                       max_modified.strftime(date_format))

    get_filmwork_id(
        tryfetchmany(
            pg_conn=conn.cursor(cursor_factory=RealDictCursor),
            lines=max_line,
            sqlreq=sql.GENRE_ID_MODIFIED.format(start_time)
        )
    )

    return set_uuids
