DELIMITER //
create trigger decrease_available_copies 
after insert on rental
for each row
begin
     if new.return_date is null then
          update school_books b
          set b.available_copies = b.available_copies-1
          where b.isbn = new.isbn and b.school_name = (
               select u.school_name 
               from user u
               where u.user_id = new.user_id);
     end if;
end//
DELIMITER ;




DELIMITER //
create trigger increase_available_copies after update on rental
for each row
begin
     if new.return_date is not null and old.return_date is null then
          update school_books b
          set b.available_copies = b.available_copies+1
          where b.isbn = new.isbn and b.school_name = (
               select u.school_name from user u
               where u.user_id = new.user_id);
     end if;
end// 
DELIMITER ;

DELIMITER //

CREATE EVENT delete_old_reservations_event
ON SCHEDULE
    EVERY 1 DAY
    STARTS CURRENT_TIMESTAMP
DO
    DELETE FROM Book_Reservation
    WHERE Reservation_Date < DATE_SUB(CURDATE(), INTERVAL 1 WEEK);

//

DELIMITER ;

