# Database Tables
this file tells you about the name, purpose, and the contents for each db tables

## all DB tables
- users (communication info and reputation)
- owners (communication info and reputation)
- stalls (location, facilities, and owner)
- slots (time and price)
- bookings (transaction records)

## purpose and content for each table

### `users`
stores the name, communication info, reputation score, and the time they created the account.

- `user_id`: auto generated integer. start from 1, and keep adding as new users joined
- `name`: string, upto 100 characters. the user's name
- `description`: string, user description
- `line_uid`: string, upto 255 characters.
- `phone`: string, upto 20 characters. the user's phone number
- `email`: string, upto 100 characters. the user's email
- `category`: string, upto 50 characters. what do they sell
- `reputation_score`: integer, default as 100. to track a user's trustworthiness. the score will drop if they frequently cancel their orders.
- `created_at`: timestamp. the exact time the user's info is written into the database.

### `owners`
stores the name, communication info, reputation score, and the time they created the account.

- `owner_id`: auto generated integer. start from 1, and keep adding as new owners joined
- `name`: string, upto 100 characters. the owner's name
- `description`: string, owner description
- `line_uid`: string, upto 255 characters.
- `phone`: string, upto 20 characters. the owner's phone number
- `email`: string, upto 100 characters. the owner's email
- `category`: string, upto 50 characters. 
- `reputation_score`: integer, default as 100. to track a owner's trustworthiness. the score will drop if they frequently cancel user's bookings.
- `created_at`: timestamp. the exact time the user's info is written into the database.


### `stalls`
stores the location name, latitude and longitude, facilities, and owner id

- `stall_id`: auto generated integer. start from 1, and keep adding as new stalls added
- `title`: string, upto 100 characters. the title or name of the stall.
- `location_name`: string, upto 100 characters. the name of the location (eg: XXX night market)
- `address`: string, upto 255 characters. the address of the location
- `lat`: decimal XXX.XXXXXX. latitude of the location
- `long`: decimal XXX.XXXXXX. longitude of the location
- `contact_info`: string, upto 100 characters. the contact info about the stall.
- `facilities`: plain text. the facilities avilable at the location (eg: water, electricity)
- `speifications`: plain text. rules or specifications of the stall (eg: no fire, noise under 90 dB)
- `owner_id`: integer, auto linked to `owner_id` on the table `owners`

### `slots`
stores the stall id, date, price, and the avilability status for the stall.
- `slot_id`: auto generated integer. start from 1, and keep adding as new stalls added
- `stall_id`: integer, auto linked to `stall_id` on the table `stalls`
- `starting_date`: date (YYYY-MM-DD), cannot be empty. the starting day to use the stall
- `ending_date`: date (YYYY-MM-DD), cannot be empty. the ending day to use the stall
- `starting_time`: time (HH:MM:SS), cannot be empty. the startiing time of a day to use the stall
- `ending_time`: time (HH:MM:SS), cannot be empty. the ending time of a day to use the stall
- `price`: integer, cannot be empty. the price for renting the stall
- `discounted_price`: integer. the discounted price for renting the stall
- `total_quantity`: integer. the total stands for this slot.
- `available_quantity` integer. the available stands for this slot.
- `status`: integer, default at 0. the status for the availability. 0: available, 1: locked


### `bookings`
stores the booked informations, including the slot, the user (renter), payment status, qr code token, and the time the deal is made.
- `booking_id`: auto generated integer. start from 1, and keep adding as new deals being made
- `user_id`: integer, auto linked to the `user_id` on the table `user`.
- `slot_id`: integer, auto linked to the `slot_id` on the table `slots`.
- `quantity`: integer, default as 1. the total stands booked.
- `payment_status`: string, upto 20 characters, default as "PENDING". to track whether the money is paid
- `payment_method`: string, upto 50 characters. the payment method of this booking.
- `qr_token`: string, upto 100 characters. the qr code token
- `created_at`: timestamp. the exact time the deal is made.
