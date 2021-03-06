// Copyright (c) 2014, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.
library test.analysis;

import 'package:unittest/unittest.dart';

import '../utils.dart';
import 'get_errors_test.dart' as get_errors_test;
import 'get_hover_test.dart' as get_hover_test;
import 'get_navigation_test.dart' as get_navigation_test;
import 'notification_analyzedFiles_test.dart'
    as notification_analyzedFiles_test;
import 'notification_errors_test.dart' as notification_errors_test;
import 'notification_highlights_test.dart' as notification_highlights_test;
import 'notification_highlights_test2.dart' as notification_highlights_test2;
import 'notification_implemented_test.dart' as notification_implemented_test;
import 'notification_navigation_test.dart' as notification_navigation_test;
import 'notification_occurrences_test.dart' as notification_occurrences_test;
import 'notification_outline_test.dart' as notification_outline_test;
import 'notification_overrides_test.dart' as notification_overrides_test;
import 'set_priority_files_test.dart' as set_priority_files_test;
import 'update_content_test.dart' as update_content_test;

/**
 * Utility for manually running all tests.
 */
main() {
  initializeTestEnvironment();
  group('analysis', () {
    get_errors_test.main();
    get_hover_test.main();
    get_navigation_test.main();
    notification_analyzedFiles_test.main();
    notification_errors_test.main();
    notification_highlights_test.main();
    notification_highlights_test2.main();
    notification_implemented_test.main();
    notification_navigation_test.main();
    notification_occurrences_test.main();
    notification_outline_test.main();
    notification_overrides_test.main();
    set_priority_files_test.main();
    update_content_test.main();
  });
}
