# ginkgo

ginkgo --focus "there should be no github repo" test.test

ginkgo --focus "GreenfieldSp" test.test

ginkgo --focus "should create XXX workflow successfully" test.test

ginkgo --label-filter="GF-E2E" test.test

--json-report=report.json --no-color