# Changelog

<!--next-version-placeholder-->

## v2.3.0 (2022-07-05)
### Feature
* Module state and 'globals' are safe. thanks, Ronny! ([`2e0d3cd`](https://github.com/ainsleymcgrath/pytest-embrace/commit/2e0d3cdbf165e193757131d563336feb386b6fb4))

### Documentation
* Remove all unused pages ([`e7edbc6`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e7edbc608df410b557649212e8453b0e98ee05bf))

## v2.2.0 (2022-07-01)
### Feature
* Specify generated comments with plain strings ([`502fe80`](https://github.com/ainsleymcgrath/pytest-embrace/commit/502fe80c616faa7a672ed0bdfac4daa52bba2a74))
* Add '--embrace-ls' flag ([`db00365`](https://github.com/ainsleymcgrath/pytest-embrace/commit/db00365169f4b501c2e4c8b88a25526f27371759))

### Fix
* **yikes:** Loop never stopped :grimace: ([`7f9f00f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/7f9f00ffee48b654fae7e1a79abf736306f1d1d3))
* Check for pep39 b/c `Annotated[]` broke create_model() ([`0eaa31c`](https://github.com/ainsleymcgrath/pytest-embrace/commit/0eaa31c2fb0e1a20ea1df306fa57434a4bc875d2))
* Exit CLI sooner ([`26f8307`](https://github.com/ainsleymcgrath/pytest-embrace/commit/26f830790e752d78fa3551cee5cd4e0eff40b584))
* Collections.abc isn't generic in 3.8 ([`391691b`](https://github.com/ainsleymcgrath/pytest-embrace/commit/391691b0c1648965c0781cd314a6e515a13ff10b))

### Documentation
* Add codegen docs ([`66a7661`](https://github.com/ainsleymcgrath/pytest-embrace/commit/66a7661b12a09cc052430a917ecaa6a096bc317e))
* Get rid of fake example; slight edit index ([`3bf5b97`](https://github.com/ainsleymcgrath/pytest-embrace/commit/3bf5b971bc9bef2c7476a34cd466ca544051e10f))

## v2.1.1 (2022-06-28)
### Fix
* Don't refer to old version of the class ([`64b539a`](https://github.com/ainsleymcgrath/pytest-embrace/commit/64b539a32e679029ef0ad9839215d294a9ea803e))

### Documentation
* Add 'Enhancing' to nav ([`e844231`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e844231b34e80907a0f9c16d96c08764afa7debe))
* First cut of the 'Enhancing Usage' section ([`4d586e8`](https://github.com/ainsleymcgrath/pytest-embrace/commit/4d586e86ab1cbb705473998474e7e662fa7ba4e3))

## v2.1.0 (2022-06-28)
### Feature
* Parser actually works now ([`3b76689`](https://github.com/ainsleymcgrath/pytest-embrace/commit/3b7668999bc052fc7613db41b23d869fa8f8a3ab))

## v2.0.0 (2022-06-28)
### Feature
* Actually marry filename derivation and table ([`da823d1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/da823d1b287d930e8bbdf3540bf94eb4400ac5cf))

### Fix
* **bug:** Once again, fix incorrect import gen ([`2b63b06`](https://github.com/ainsleymcgrath/pytest-embrace/commit/2b63b06c28ae4f25ba4a75adde76fd91049cdfed))
* Simplify type ([`b888196`](https://github.com/ainsleymcgrath/pytest-embrace/commit/b888196d2408ec8d571f6b445726a43e1f95aee9))

### Breaking
* DeriveFromFileName() is effectively deprecated in favor of derive_from_filename()  ([`7621aee`](https://github.com/ainsleymcgrath/pytest-embrace/commit/7621aee7a49079c9d8e3f8a6c6409a2a68f2645b))

### Documentation
* First portion of how-to + nav ([`a62721d`](https://github.com/ainsleymcgrath/pytest-embrace/commit/a62721da1cb5af7cbca07ac8f2011293aad92b3d))
* Fix title to be not redundant ([`abf8416`](https://github.com/ainsleymcgrath/pytest-embrace/commit/abf8416d2c82229261d5d59e97c3b3dc4ce5eef0))
* A little more color in About ([`593b36e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/593b36ebb4a75a6390c01d00faaf7dcf85a8f4b4))
* Fix typo ([`513f60f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/513f60fda51c89b15bc15ef5fe11f7f597dfe20d))
* Fix invalid config ([`432ab79`](https://github.com/ainsleymcgrath/pytest-embrace/commit/432ab79662c34aa8f9a968b95336665081ecf166))

## v1.0.2 (2022-06-26)
### Fix
* **bug:** Stop generating invalid code ([`fdbe903`](https://github.com/ainsleymcgrath/pytest-embrace/commit/fdbe9038bac8c4fa9eeefc0888cebb71e53b13d2))

### Documentation
* Favicon, fix smushed logo ([`1cde606`](https://github.com/ainsleymcgrath/pytest-embrace/commit/1cde60619c0283d96deda1a1a982a30c8f33de98))
* Migrate some old content to mkdocs ([`897ef85`](https://github.com/ainsleymcgrath/pytest-embrace/commit/897ef85a0a97efd23395c928192a72e800596c31))
* Readme sends you to docs site ([`b01489c`](https://github.com/ainsleymcgrath/pytest-embrace/commit/b01489c521c564ca385accd7a990ab0ceddee735))
* Add logos (messy) ([`c4bf852`](https://github.com/ainsleymcgrath/pytest-embrace/commit/c4bf8523fad5d35225ffbb2fcc691d2ee6a9713c))
* Break ground ([`c5ff887`](https://github.com/ainsleymcgrath/pytest-embrace/commit/c5ff887702208b73199d55f55a2c0814c05140fb))
* More missing details ([`fd83a4c`](https://github.com/ainsleymcgrath/pytest-embrace/commit/fd83a4c8ecc101b9194eb6da45b6028391511043))
* Add proper TOC ([`bac5d52`](https://github.com/ainsleymcgrath/pytest-embrace/commit/bac5d526d29cc584a5b22d09738bc12c57408c1e))

## v1.0.1 (2022-06-24)
### Fix
* Correct validation of table cases; expand trickles() ([`0ba1141`](https://github.com/ainsleymcgrath/pytest-embrace/commit/0ba1141bbf96818b74ddc0dcb98f929c0cbf9b12))

### Documentation
* Flatten headings, add TOC ([`0914d5a`](https://github.com/ainsleymcgrath/pytest-embrace/commit/0914d5a7573c3702ce3cd9ae9b1361400a9b5217))
* Add links, reword a bit ([`17066c7`](https://github.com/ainsleymcgrath/pytest-embrace/commit/17066c7bc37c203e025216dbbad0fab08c9068a3))
* Better description ([`206a58d`](https://github.com/ainsleymcgrath/pytest-embrace/commit/206a58d1edc74b0997ab065a23e2606ddd2e8bc3))

## v1.0.0 (2022-06-24)
### Breaking
* the name change is in a user-facing namespace  ([`7d64d97`](https://github.com/ainsleymcgrath/pytest-embrace/commit/7d64d9727f0449e76607e758fca7d800fbe8119b))

## v0.4.2 (2022-06-23)
### Fix
* Add fine-grained trickles() control ([`f856e59`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f856e59d2724fbc9d5cdd5e4b7e5fbdcb5ff5447))

## v0.4.1 (2022-06-23)
### Fix
* **terrible oversight:** Actually _use_ the case artifact ([`fa8a0b5`](https://github.com/ainsleymcgrath/pytest-embrace/commit/fa8a0b5ece0a7232155ca3ee7958105c183f90fe))

## v0.4.0 (2022-06-23)
### Feature
* Introducing: DeriveNameFromFile() ([`754b446`](https://github.com/ainsleymcgrath/pytest-embrace/commit/754b44607ac012fb66bffe19aa73951432656164))

### Fix
* Poorly formed tests + compatibility ([`ce98b88`](https://github.com/ainsleymcgrath/pytest-embrace/commit/ce98b88820f81d04d119080c055e1b28677bf3c8))
* Handle nested name derive w plugin test ([`108b2d1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/108b2d1dd7e5ff903f2c4a580859c938e0e53b80))
* Remove breakpoint ([`5169de5`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5169de502da3af786ea037a754526000f1f9f68b))

## v0.3.0 (2022-06-23)
### Feature
* First ever annotation -> Comment() ([`f53a202`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f53a202124e037761a027522f8acca07db2741c6))
* 'trickle down' attrs ([`496cf4c`](https://github.com/ainsleymcgrath/pytest-embrace/commit/496cf4c8a8883252cc02fd0e5e41b73356579d28))

### Fix
* Support stuff properly ([`1a70f19`](https://github.com/ainsleymcgrath/pytest-embrace/commit/1a70f191c9f1e713f5bdea6e311e74d4998b0930))

## v0.2.0 (2022-06-22)
### Feature
* Pytest flag for code gen ([`07e0241`](https://github.com/ainsleymcgrath/pytest-embrace/commit/07e0241a184fd15eb1b73ab4fae1576493bd2a53))

### Fix
* **ci:** Missing option ([`2655b0f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/2655b0f314d92dc07af74be02181b6ffd91cb6ed))

## v0.1.0 (2022-06-21)
### Feature
* Type checking ([`230d3d4`](https://github.com/ainsleymcgrath/pytest-embrace/commit/230d3d4302189c50234bab92ce0bfc0904159ddb))

## v0.0.2-beta.6 (2022-06-20)


## v0.0.2-beta.5 (2022-06-20)


## v0.0.2-beta.4 (2022-06-20)


## v0.0.1 (2022-06-20)
### Fix
* **ci:** Don't do GH releases ([`3f8bab5`](https://github.com/ainsleymcgrath/pytest-embrace/commit/3f8bab5aaf763e6ab9a0b6a6b7ac9be7470e37f6))

## v0.0.1 (2022-06-20)
### Fix
* Add py.typed marker @beta ([`3e7ba7e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/3e7ba7e0b1183aa8c3ed903b8f534b38111226a6))

## v0.0.2-beta.1 (2022-06-20)
### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))
* **ci:** Set env properly ([`49f9498`](https://github.com/ainsleymcgrath/pytest-embrace/commit/49f9498bf13de4b59f9b419a15aa5e54dbb38511))
* **release:** Use env properly in gh actions ([`e804b01`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e804b0174ad4d2be6bb5f458a9e01497207ca8d1))
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

### Documentation
* Write down more aspirations ([`023610e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/023610ea274f97f34730162df2b3f51bbc9d7798))
* Write down more aspirations ([`65299f1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/65299f16c0cf098fb37d16129d28b2fe49fc7974))

## v0.1.0-beta.1 (2022-06-20)
### Feature
* Semantic release? ([`f0ec712`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f0ec7129d89885df404eec8cb474ad4d7d2d7790))

### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))
* **ci:** Set env properly ([`49f9498`](https://github.com/ainsleymcgrath/pytest-embrace/commit/49f9498bf13de4b59f9b419a15aa5e54dbb38511))
* **release:** Use env properly in gh actions ([`e804b01`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e804b0174ad4d2be6bb5f458a9e01497207ca8d1))
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

### Documentation
* Write down more aspirations ([`023610e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/023610ea274f97f34730162df2b3f51bbc9d7798))
* Write down more aspirations ([`65299f1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/65299f16c0cf098fb37d16129d28b2fe49fc7974))

## v0.0.2-beta.1 (2022-06-20)
### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))
* **ci:** Set env properly ([`49f9498`](https://github.com/ainsleymcgrath/pytest-embrace/commit/49f9498bf13de4b59f9b419a15aa5e54dbb38511))
* **release:** Use env properly in gh actions ([`e804b01`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e804b0174ad4d2be6bb5f458a9e01497207ca8d1))
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

### Documentation
* Write down more aspirations ([`023610e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/023610ea274f97f34730162df2b3f51bbc9d7798))
* Write down more aspirations ([`65299f1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/65299f16c0cf098fb37d16129d28b2fe49fc7974))

## v0.1.0-beta.1 (2022-06-20)
### Feature
* Semantic release? ([`f0ec712`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f0ec7129d89885df404eec8cb474ad4d7d2d7790))

### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))
* **ci:** Set env properly ([`49f9498`](https://github.com/ainsleymcgrath/pytest-embrace/commit/49f9498bf13de4b59f9b419a15aa5e54dbb38511))
* **release:** Use env properly in gh actions ([`e804b01`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e804b0174ad4d2be6bb5f458a9e01497207ca8d1))
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

### Documentation
* Write down more aspirations ([`023610e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/023610ea274f97f34730162df2b3f51bbc9d7798))
* Write down more aspirations ([`65299f1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/65299f16c0cf098fb37d16129d28b2fe49fc7974))

## v0.0.2-beta.1 (2022-06-20)


## v0.0.2 (2022-06-20)
### Feature
* Semantic release? ([`f0ec712`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f0ec7129d89885df404eec8cb474ad4d7d2d7790))

### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))
* **ci:** Set env properly ([`49f9498`](https://github.com/ainsleymcgrath/pytest-embrace/commit/49f9498bf13de4b59f9b419a15aa5e54dbb38511))
* **release:** Use env properly in gh actions ([`e804b01`](https://github.com/ainsleymcgrath/pytest-embrace/commit/e804b0174ad4d2be6bb5f458a9e01497207ca8d1))
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

### Documentation
* Write down more aspirations ([`023610e`](https://github.com/ainsleymcgrath/pytest-embrace/commit/023610ea274f97f34730162df2b3f51bbc9d7798))
* Write down more aspirations ([`65299f1`](https://github.com/ainsleymcgrath/pytest-embrace/commit/65299f16c0cf098fb37d16129d28b2fe49fc7974))

## v0.0.2-beta.1 (2022-06-20)


## v0.0.1 (2022-06-20)
### Fix
* Add poetry to deps in release ([`1149963`](https://github.com/ainsleymcgrath/pytest-embrace/commit/114996333439810d8c3837a8c3f987c61ae39b96))

## v0.0.1 (2022-06-20)
### Fix
* Remove unused (big) dep ([`5773a2f`](https://github.com/ainsleymcgrath/pytest-embrace/commit/5773a2ff650c585e4ab320f5e7b1386224bb4e0b))

## v0.1.0-beta.1 (2022-06-20)
### Feature
* Semantic release? ([`f0ec712`](https://github.com/ainsleymcgrath/pytest-embrace/commit/f0ec7129d89885df404eec8cb474ad4d7d2d7790))
