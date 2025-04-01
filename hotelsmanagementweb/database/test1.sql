CREATE DATABASE my_classicmodels;
USE my_classicmodels;

CREATE TABLE orders (
    orderNumber INT(11) PRIMARY KEY AUTO_INCREMENT,
    orderDate DATETIME,
    requiredDate DATETIME,
    shippedDate DATETIME,
    status VARCHAR(15),
    comments TEXT,
    customerNumber INT(11));

CREATE TABLE productlines (
    productLine VARCHAR(50) PRIMARY KEY,
    textDescription VARCHAR(4000),
    htmlDescription MEDIUMTEXT,
    image MEDIUMBLOB
);

CREATE TABLE products (
    productCode VARCHAR(15) PRIMARY KEY,
    productName VARCHAR(70),
    productLine VARCHAR(50),
    productScale VARCHAR(10),
    productVendor VARCHAR(50),
    productDescription TEXT,
    quantityInStock SMALLINT(6),
    buyPrice DOUBLE,
    FOREIGN KEY (productLine) 
        REFERENCES productlines(productLine)
        ON UPDATE CASCADE
);

CREATE TABLE orderdetails (
    orderNumber INT(11),
    productCode VARCHAR(15),
    quantityOrdered INT(11),
    priceEach DOUBLE,
    orderLineNumber SMALLINT(6),
    PRIMARY KEY (orderNumber, productCode),
    FOREIGN KEY (orderNumber) 
        REFERENCES orders(orderNumber)
        ON UPDATE CASCADE,
    FOREIGN KEY (productCode) 
        REFERENCES products(productCode)
        ON UPDATE CASCADE
);

show tables;

select * from orders; 