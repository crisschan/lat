-- database: ../database/petstore.db


CREATE TABLE pets (
  "id" integer PRIMARY KEY autoincrement ,
  "name"  varchar(255) DEFAULT NULL,
  "category_id" integer,
  "photourls" varchar(255) DEFAULT NULL,
  "tags" VARCHAR(255),
  "status" VARCHAR(255) NOT NULL
);

CREATE TABLE category(
    "id" integer PRIMARY KEY autoincrement ,
    "name"  VARCHAR(255) NOT NULL
);

CREATE TABLE user(
  "id" integer PRIMARY KEY autoincrement ,
  "username"  VARCHAR(255) NOT NULL,
  "firstName"  VARCHAR(255) NOT NULL,
  "lastName"  VARCHAR(255) NOT NULL,
  "email" VARCHAR(255) NOT NULL,
  "password"  VARCHAR(255) NOT NULL,
  "phone"  VARCHAR(255) NOT NULL,
  "userStatus" integer
);

CREATE TABLE "order"(
      "id" integer PRIMARY KEY autoincrement,
      "pet_id" INTEGER,
      "shipdate" date,
      "quantity" INTEGER,
      "complete" Boolean,
      "status" VARCHAR(255) NOT NULL

);

INSERT INTO `order` (id, pet_id, shipdate, quantity, complete, status)
VALUES
(1, 101, '2023-04-01', 1, 0, 'placed'),
(2, 102, '2023-04-02', 2, 0, 'placed'),
(3, 103, '2023-04-03', 3, 0, 'placed'),
(4, 104, '2023-04-04', 4, 0, 'placed'),
(5, 105, '2023-04-05', 5, 0, 'placed'),
(6, 106, '2023-04-06', 6, 0, 'placed'),
(7, 107, '2023-04-07', 7, 0, 'placed'),
(8, 108, '2023-04-08', 8, 0, 'placed'),
(9, 109, '2023-04-09', 9, 0, 'placed'),
(10, 110, '2023-04-10', 10, 0, 'placed');

UPDATE `pets`
SET status = 'sold'
WHERE id IN (SELECT pet_id FROM `order` WHERE id BETWEEN 1 AND 10);