# Learn Blockchains by Building One

## URLs
- https://hackernoon.com/learn-blockchains-by-building-one-117428612f46
- https://qiita.com/hidehiro98/items/841ece65d896aeaa8a2a

## Requirements

- Flask==1.0.2
- requests==2.21.0

## Github

- https://github.com/dvf/blockchain

## Run
```
$ python bloackchain.py
```

## Commands
### Mining
```
$ curl http://localhost:5000/mine
```

## New Transaction
```
$ curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "recipient": "someone-other-address",
 "amount": 5
}' "http://localhost:5000/transactions/new"
```

## Get full chain
```
$ curl http://localhost:5000/chain

```