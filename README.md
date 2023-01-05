# extend_take_home

###

### Step 1: Create .env file

```
EMAIL=<email>
PASSWORD=<password>
BASE_URL=https://api.paywithextend.com/
```

### Step 2: Build the docker image and containers

```
docker-compose up -d --build
```

### Step 3: Hit endpoints at http://localhost:5000

### Endpoints

- /credit_card/sign_in
- /credit_card/get_user_info
- /credit_card/get_virtual_cards
- /credit_card/transactions_min
- /credit_card/transaction/[transaction_id]
- /credit_card/transactions_detailed
