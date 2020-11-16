CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE spatial.areas ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE spatial.contexts ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE object.finds ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE options.material_category ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE object.finds ADD COLUMN user_id integer NULL;

ALTER TABLE ojbect.finds ADD CONSTRAINT user_id_object_find_fkey
FOREIGN KEY (user_id) REFERENCES django.users.user_id(id)
ON UPDATE CASCADE ON DELETE SET NULL;

CREATE INDEX object_find_user_id ON object.finds(user_id);
