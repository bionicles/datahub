# This example illustrates how to extract table names from nested
# SELECT statements.

# See:
# http://groups.google.com/group/sqlparse/browse_thread/thread/b0bd9a022e9d4895

tsql = """
select K.a from (select H.b from (select G.c from (select F.d from
(select E.e from A, B, C, D, E), F), G), H), I, J, K;
"""

tsql ='create table X ()'

import sqlparse
import re
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML, DDL

def is_subselect(parsed):
    if not parsed.is_group():
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False

def is_create(parsed):
    if not parsed.is_group():
        return False
    for item in parsed.tokens:
        if item.ttype is DDL and item.value.upper() == 'CREATE':
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    from_create = False
    for item in parsed.tokens:
        if item.value.upper() == 'UPDATE':
          print "UP", item, item.ttype
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif from_create:
                #TODO parse out table name from funtion?
                yield str(item).split("(",1)[0].strip()
            else:
                yield item

        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True
        elif item.ttype is Keyword and item.value.upper() == 'INTO':
            #TODO hack this returns values also
            from_seen = True   
        elif item.ttype is Keyword.DML and item.value.upper() == 'UPDATE':
            print "update"
            from_seen = True    
        elif item.ttype is DDL and item.value.upper() == 'CREATE':
            from_create = True
        elif from_create and item.value.upper() == 'TABLE':
            from_seen = True
        

def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, Identifier):
            yield item.get_name()
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        elif isinstance(item, str):
            if item.strip() != '' and re.search('\w+',item):
              yield item
        elif item.ttype is Keyword:
            yield item.value

def extract_tables(sql):
    stream = extract_from_part(sqlparse.parse(sql)[0])
    return list(extract_table_identifiers(stream))

if __name__ == '__main__':
    csql = 'create table students ( s_id integer, name varchar(50));'
    print csql
    print 'Tables: %s' % ', '.join(extract_tables(csql))
    usql = "update students set name = 'ae' where id = 1"
    print usql
    print 'Tables: %s' % ', '.join(extract_tables(usql))
    