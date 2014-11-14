from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
share = Table('share', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=140)),
    Column('desc', TEXT),
    Column('timestamp', TIMESTAMP),
    Column('number_people', SMALLINT),
    Column('price_total', SMALLINT),
    Column('price_per_share', SMALLINT),
    Column('user_id', INTEGER),
    Column('community_id', INTEGER),
)

share = Table('share', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=140)),
    Column('desc', Text),
    Column('timestamp', DateTime),
    Column('number_people', SmallInteger),
    Column('price_total', SmallInteger),
    Column('price_per_people', SmallInteger),
    Column('user_id', Integer),
    Column('community_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['share'].columns['price_per_share'].drop()
    post_meta.tables['share'].columns['price_per_people'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['share'].columns['price_per_share'].create()
    post_meta.tables['share'].columns['price_per_people'].drop()
