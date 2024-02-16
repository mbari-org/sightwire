# sightwire Changelog

## [1.1.1](http://bitbucket.org/compas-sw/sightwire/compare/v1.1.0...v1.1.1) (2024-02-16)


### Bug Fixes

* switch to port 8080 and mantis nginx conf, fix bulk load and other simplification to align with deployment on atuncita ([c52f205](http://bitbucket.org/compas-sw/sightwire/commits/c52f2057c711386aa99de8f46840ee3dcdd2646e))

# [1.1.0](http://bitbucket.org/compas-sw/sightwire/compare/v1.0.0...v1.1.0) (2024-02-15)


### Bug Fixes

* correct f-string ([54e94af](http://bitbucket.org/compas-sw/sightwire/commits/54e94af5111bf1249abcc0be926d8165fbc8ec9a))


### Features

* added realtime simulated load from livestream with watchdog ([64599fe](http://bitbucket.org/compas-sw/sightwire/commits/64599fee4eef894a4ec41043173a5fab08df79ce))

# 1.0.0 (2024-02-08)


### Features

* added livestream simulation load, bulk load and Stereo state tables for stereo image association. This removes image stereo concat creation in favor of state table to reduce storage size ([9a25d2c](http://bitbucket.org/compas-sw/sightwire/commits/9a25d2c750bf46e0ce872ca772c3ed233d9faae0))
* initial commit ([fc82329](http://bitbucket.org/compas-sw/sightwire/commits/fc8232985ef8824994c076a4a73cf7f8ffc19ade))
