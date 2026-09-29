CREATE TABLE Users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    role ENUM(
        'Chief',
        'Manager',
        'Receptionist',
        'Accountant'
    ) NOT NULL,
    status ENUM('Active','Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Guests(
    guest_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15),
    address VARCHAR(255),
    id_proof VARCHAR(50)
);
CREATE TABLE Rooms(
    room_id INT PRIMARY KEY,
    room_type VARCHAR(50),
    price DECIMAL(10,2),
    status ENUM(
        'Available',
        'Booked',
        'Cleaning',
        'Maintenance'
    ) DEFAULT 'Available'
);
CREATE TABLE Bookings(
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT,
    room_id INT,
    check_in DATE,
    check_out DATE,
    booking_status ENUM(
        'Booked',
        'Checked In',
        'Checked Out',
        'Cancelled'
    ) DEFAULT 'Booked',

    FOREIGN KEY(guest_id)
    REFERENCES Guests(guest_id),

    FOREIGN KEY(room_id)
    REFERENCES Rooms(room_id)
);
CREATE TABLE Payments(
    payment_id INT AUTO_INCREMENT PRIMARY KEY,

    booking_id INT,

    amount DECIMAL(10,2),

    payment_date DATE,

    method ENUM(
        'Cash',
        'UPI',
        'Credit Card',
        'Debit Card',
        'Net Banking'
    ),

    payment_status ENUM(
        'Paid',
        'Pending'
    ) DEFAULT 'Paid',

    FOREIGN KEY(booking_id)
    REFERENCES Bookings(booking_id)
);
INSERT INTO Users
(
full_name,
username,
password,
email,
phone,
role
)
VALUES
(
'Chief Admin',
'chief',
'#Harika@123.',
'chief@stayverse.com',
'9876543210',
'Chief'
);
INSERT INTO Users
(full_name,username,password,email,phone,role)
VALUES
('Uma Mahesh','mahi123','Mahesh@2426','mahesh@gmail.com','7013256315','Manger');


INSERT INTO Guests(guest_id,name,email,phone) VALUES
(1,'John Doe','john@example.com','9876543210'),
(2,'Alice Ray','alice@example.com','8765432109'),
(3,'David Smith','david@example.com','7654321098'),
(4,'Maria Lee','maria@example.com','6543210987'),
(5,'Rahul Jain','rahul@example.com','9123456780'),
(6,'Neha Sharma','neha@example.com','9988776655'),
(7,'Sanjay Patel','sanjay@example.com','8877665544'),
(8,'Priya Mehta','priya@example.com','7766554433'),
(9,'Aman Verma','aman@example.com','6655443322'),
(10,'Rita Kapoor','rita@example.com','5544332211'),
(11,'Karan Bhatt','karan@example.com','9988776654'),
(12,'Anjali Singh','anjali@example.com','8899001122'),
(13,'Vikram Reddy','vikram@example.com','8800112233'),
(14,'Kriti Sen','kriti@example.com','9900112233'),
(15,'Ishaan Khurana','ishaan@example.com','9112233445'),
(16,'Meena Kumari','meena@example.com','9223344556'),
(17,'Arjun Nair','arjun@example.com','9334455667'),
(18,'Divya Rao','divya@example.com','9445566778'),
(19,'Tanya Joshi','tanya@example.com','9556677889'),
(20,'Manoj Sinha','manoj@example.com','9667788990');

INSERT INTO Rooms(room_id,room_type,price,status) VALUES
(101,'Single',1500.00,'Available'),
(102,'Double',2500.00,'Booked'),
(103,'Suite',4500.00,'Available'),
(104,'Deluxe',3500.00,'Booked'),
(105,'Economy',1000.00,'Available'),
(106,'Single AC',1600.00,'Booked'),
(107,'Double AC',2700.00,'Booked'),
(108,'Luxury Suite',5000.00,'Available'),
(109,'Deluxe AC',3600.00,'Booked'),
(110,'Budget',900.00,'Available'),
(111,'Family Suite',5500.00,'Available'),
(112,'Presidential Suite',9000.00,'Available'),
(113,'Business Class',4200.00,'Booked'),
(114,'Studio Room',2800.00,'Available'),
(115,'Penthouse',7500.00,'Available'),
(116,'Compact',950.00,'Available'),
(117,'Garden View',3000.00,'Booked'),
(118,'City View',3200.00,'Available'),
(119,'Queen Deluxe',3800.00,'Booked'),
(120,'Twin Room',2600.00,'Available');

INSERT INTO Bookings(booking_id,guest_id,room_id,check_in,check_out) VALUES
(1,1,101,'2026-01-05','2026-01-07'),
(2,2,102,'2026-01-18','2026-01-20'),
(3,3,104,'2026-02-02','2026-02-04'),
(4,4,106,'2026-02-15','2026-02-17'),
(5,5,107,'2026-03-01','2026-03-03'),
(6,6,109,'2026-03-14','2026-03-16'),
(7,7,113,'2026-03-28','2026-03-30'),
(8,8,117,'2026-04-05','2026-04-07'),
(9,9,119,'2026-04-18','2026-04-20'),
(10,10,105,'2026-05-02','2026-05-04'),
(11,11,103,'2026-05-14','2026-05-16'),
(12,12,114,'2026-05-27','2026-05-29'),
(13,13,118,'2026-06-04','2026-06-06'),
(14,14,120,'2026-06-12','2026-06-14'),
(15,15,116,'2026-06-18','2026-06-20'),
(16,16,110,'2026-06-24','2026-06-26'),
(17,17,108,'2026-07-01','2026-07-03'),
(18,18,112,'2026-07-08','2026-07-10'),
(19,19,111,'2026-07-15','2026-07-17'),
(20,20,115,'2026-07-22','2026-07-24');

INSERT INTO Payments(payment_id,booking_id,amount,payment_date,method) VALUES
(1,1,3000.00,'2026-01-05','Credit Card'),
(2,2,5000.00,'2026-01-18','Cash'),
(3,3,7000.00,'2026-02-02','UPI'),
(4,4,9000.00,'2026-02-15','Credit Card'),
(5,5,5400.00,'2026-03-01','Net Banking'),
(6,6,7200.00,'2026-03-14','Cash'),
(7,7,8800.00,'2026-03-28','UPI'),
(8,8,6500.00,'2026-04-05','Credit Card'),
(9,9,7600.00,'2026-04-18','Cash'),
(10,10,2000.00,'2026-05-02','Credit Card'),
(11,11,4500.00,'2026-05-14','UPI'),
(12,12,2800.00,'2026-05-27','Credit Card'),
(13,13,3200.00,'2026-06-04','Net Banking'),
(14,14,2600.00,'2026-06-12','Cash'),
(15,15,1900.00,'2026-06-18','UPI'),
(16,16,1100.00,'2026-06-24','Credit Card'),
(17,17,5000.00,'2026-07-01','Cash'),
(18,18,9200.00,'2026-07-08','UPI'),
(19,19,5600.00,'2026-07-15','Net Banking'),
(20,20,7500.00,'2026-07-22','Credit Card');

SELECT MONTH(payment_date) AS month,
SUM(amount) AS revenue
FROM Payments
GROUP BY MONTH(payment_date);

SELECT MONTH(check_in) AS month,
COUNT(*) AS total
FROM Bookings
GROUP BY MONTH(check_in);

SELECT status,
COUNT(*) total
FROM Rooms
GROUP BY status;

SELECT method,
COUNT(*) total
FROM Payments
GROUP BY method;

