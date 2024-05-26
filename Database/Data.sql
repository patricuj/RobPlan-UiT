-- SQL-script for å sette inn data i `Users` og `Missions` tabellene i databasen `myDb`.
-- Brukernavn: 'testbruker', passord: 'test'

USE myDb ;

INSERT INTO `myDb`.`Users` (`Username`, `Password`) VALUES ('testbruker', 'scrypt:32768:8:1$8ONrsyhMWZqqh3Ok$c6a58479c6ad266c206be9d73d5ea368d49027e9f0ab51c2c0b3a5c8a71f0329ccf27252e4fc8b93d15a0fc3150cf51d30411136bb56e37c95eaab352a21cb36');

INSERT INTO `myDb`.`Missions` (`MissionName`, `MissionData`, `IsAvailable`, `Port`) VALUES
('Maintenance level 1', '{"id":"Maintenance level 1","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 1, 3000),
('Base test', '{"id":"Base test","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 1, 4000),
('Pipeline valve 2 inspection', '{"id":"Pipeline valve 2 inspection","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 1, 6000),
('Maintenance level 3', '{"id":"Maintenance level 3","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 0, 3000),
('Maintenance level 2', '{"id":"Maintenance level 2","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 0, 4000),
('Pipeline valve inspection', '{"id":"Pipeline valve inspection","tasks":[{"steps":[{"type":"drive_to_pose","pose":{"position":{"x":-2,"y":-2,"z":0,"frame":"asset"},"orientation":{"x":0,"y":0,"z":0.4794255,"w":0.8775826,"frame":"asset"},"frame":"asset"}},{"type":"take_image","target":{"x":2,"y":2,"z":0,"frame":"robot"}}]}]}', 0, 6000);