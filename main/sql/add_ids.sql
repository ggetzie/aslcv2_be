CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE spatial.areas ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE spatial.contexts ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE object.finds ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();
ALTER TABLE options.material_category ADD COLUMN id uuid UNIQUE DEFAULT uuid_generate_v4 ();