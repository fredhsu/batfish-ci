# Batfish example
This is an example of querying a list of switches to see if the proposed config will allow access to a particular web server. If not, exit code will be 1, otherwise exit code is 0.

## Running demo
docker build . -t pybatfish
docker run --rm pybatfish
docker run -v /Users/fredlhsu/python/batfish/networks:/batfish/networks --rm pybatfish

## TODO
- [x] Externalize directory that holds configs - use -v when executing - remove copy commands
- [ ] Externalize directory that holds hosts - use -v when executing - remove copy commands
- [x] Pulls devices from list
- [x] Pulls hosts that should be reachable from permit list
- [x] Pulls hosts that should be reachable external source
- [ ] Add test cases
- [ ] Remove keys
- [ ] Move code to functions
- [ ] Use requirements in dockerfile
- [ ] Switch container to alpine





