# Changelog

## 0.0.1 (2026-11-28)


### Features

* **engine:** renew the database server's certificate before it expires ([#17](https://github.com/cocreiamo/anima/issues/17)) ([f7f6e48](https://github.com/cocreiamo/anima/commit/f7f6e488631e6468568b43c5350a0fe644d4a633))
* make the decision records from the organization's template (TASK-65) ([#31](https://github.com/cocreiamo/anima/issues/31)) ([2025978](https://github.com/cocreiamo/anima/commit/2025978a98677b12a84c5307e1aaaef7d0027180))
* **mirror:** copy every base image into the organization's mirror, by digest (R160 to R164, GAP-060, TASK-43) ([#39](https://github.com/cocreiamo/anima/issues/39)) ([3a7152e](https://github.com/cocreiamo/anima/commit/3a7152ec3830d4b60eac1dd6d59b154394957bf5))
* read the configurator's data files with an adopted YAML parser ([#11](https://github.com/cocreiamo/anima/issues/11)) ([71dcd1b](https://github.com/cocreiamo/anima/commit/71dcd1b1106420b7e036e31071172cc45ec67c92))
* run the system tests on pull requests and publish the verified engine image (R24, R114, R115) ([#13](https://github.com/cocreiamo/anima/issues/13)) ([e4a5b4f](https://github.com/cocreiamo/anima/commit/e4a5b4f7cc262f3113c6ede84ef0b3587f3ea9c9))
* set up the repository, the requirements model and the engine image ([#1](https://github.com/cocreiamo/anima/issues/1)) ([593c667](https://github.com/cocreiamo/anima/commit/593c66717b6e99386c71f78263b08c1a1114ab51))


### Bug Fixes

* ask the registry whether the version tag exists, and stop when it cannot say (R115, PM-013) ([#38](https://github.com/cocreiamo/anima/issues/38)) ([11b1cfe](https://github.com/cocreiamo/anima/commit/11b1cfe1ae85a68db19a559f3748edd0ac5b90e2))
* export the model once when several tasks ask at the same time ([#3](https://github.com/cocreiamo/anima/issues/3)) ([e7c8139](https://github.com/cocreiamo/anima/commit/e7c813948e5ada7a2bd44e1e1d065286a39de580))
* keep releases in the 0.0 series, starting at 0.0.1 ([#4](https://github.com/cocreiamo/anima/issues/4)) ([97f0811](https://github.com/cocreiamo/anima/commit/97f0811cfbd7acdd3c11c631b112e8ace65649b8))
* leave the changelog the release tool writes out of the formatter (R155, PM-012) ([#36](https://github.com/cocreiamo/anima/issues/36)) ([2104bb8](https://github.com/cocreiamo/anima/commit/2104bb834de2d708ee84b1afe2e0bbe6566f711d))
* make format and test exclude each other with one lock (TASK-83, PM-006) ([#10](https://github.com/cocreiamo/anima/issues/10)) ([484aa59](https://github.com/cocreiamo/anima/commit/484aa5952794c6e42db837a3385e8806d76f02d1))
* make the system tests repeatable ([#12](https://github.com/cocreiamo/anima/issues/12)) ([ea7e5d9](https://github.com/cocreiamo/anima/commit/ea7e5d9378e362e3048c13ff1258616308717790))
* recover the secret store's first start after an abrupt stop (R42, PM-009) ([#23](https://github.com/cocreiamo/anima/issues/23)) ([0f48c48](https://github.com/cocreiamo/anima/commit/0f48c48e0833b692182be424f60ef24173094da0))
* refresh the cache of the inner images on pushes to main (R125, PM-010) ([#27](https://github.com/cocreiamo/anima/issues/27)) ([1a2ee8a](https://github.com/cocreiamo/anima/commit/1a2ee8aa99d10f78799b27268c1f0d34c2086ba6))
* render generated lists by name so open pull requests do not conflict in them (R150, PM-011) ([#33](https://github.com/cocreiamo/anima/issues/33)) ([faa2e97](https://github.com/cocreiamo/anima/commit/faa2e9764d13a27d040b44a4cb2ae98a6cd10e8c))
* **renovate:** follow OpenTofu for the configurator's pin (R120, R121, R122) ([#24](https://github.com/cocreiamo/anima/issues/24)) ([0026a2e](https://github.com/cocreiamo/anima/commit/0026a2ea6cfe07d288d6a30a37530e27e1688f53))


### Performance Improvements

* **tests:** run independent subprocesses together to keep the check inside R55 ([#32](https://github.com/cocreiamo/anima/issues/32)) ([ed8cd36](https://github.com/cocreiamo/anima/commit/ed8cd36848ef4c0d189bb702c5b1c05b0d94cef0))
