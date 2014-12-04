from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
join_share = Table('join_share', post_meta,
    Column('user_id', Integer, primary_key=True, nullable=False),
    Column('share_id', Integer, primary_key=True, nullable=False),
)

share = Table('share', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=140)),
    Column('desc', TEXT),
    Column('timestamp', TIMESTAMP),
    Column('number_people', SMALLINT),
    Column('price_total', SMALLINT),
    Column('user_id', INTEGER),
    Column('community_id', INTEGER),
    Column('price_per_people', SMALLINT),
    Column('people_in', SMALLINT),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['join_share'].create()
    pre_meta.tables['share'].columns['people_in'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['join_share'].drop()
    pre_meta.tables['share'].columns['people_in'].create()
