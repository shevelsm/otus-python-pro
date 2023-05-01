from datetime import datetime
import unittest

import log_analyzer


class LogAnalyzerTest(unittest.TestCase):
    def test_gz_log(self):
        config = log_analyzer.get_config_values(log_analyzer.config, "config.ini")
        config["DEFAULT"]["LOG_DIR"] = "./test/gz_log"
        self.assertEqual(
            log_analyzer.get_the_last_log_file(config),
            log_analyzer.LastLogFile(
                "./test/gz_log/nginx-access-ui.log-20180830.gz", datetime(2018, 8, 30)
            ),
        )

    def test_correct_log_line(self):
        line = (
            "12.196.116.33 -  - [29/Jun/2017:03:50:22 +0300] "
            '"GET /api/v2/banner/356256 HTTP/1.1" 200 927 "-" '
            '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" '
            '"1498697422-2190034393-4708-9752759" "dc7161be3" 0.153'
        )
        request = log_analyzer.handle_log_line(line)
        self.assertEqual(request, log_analyzer.LogLine("/api/v2/banner/356256", 0.153))

    def test_incorrect_log_line(self):
        line = (
            "31.198.135.25 -  - [01/Jun/2018:10:15:47 +0300] "
            '"HEAD /slots/3938/ HTTP/1.1" 302 0 "-" '
            '"Microsoft Office Word 2013" "-" '
            '"3497420589-244168997-4777-11316920" "-" 0.ABC0'
        )
        request = log_analyzer.handle_log_line(line)
        self.assertIsNone(request.url)
