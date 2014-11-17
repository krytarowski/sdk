// Copyright (c) 2014, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

import '../../descriptor.dart' as d;
import '../../test_pub.dart';

const TRANSFORMER = """
import 'dart:async';

import 'package:barback/barback.dart';

class DartTransformer extends Transformer {
  DartTransformer.asPlugin();

  String get allowedExtensions => '.in';

  void apply(Transform transform) {
    transform.addOutput(new Asset.fromString(
        new AssetId("foo", "bin/script.dart"),
        "void main() => print('generated');"));
  }
}
""";

main() {
  initConfig();
  withBarbackVersions("any", () {
    integration('runs a global script generated by a transformer', () {
      makeGlobalPackage("foo", "1.0.0", [d.pubspec({
          "name": "foo",
          "version": "1.0.0",
          "transformers": ["foo/src/transformer"]
        }),
            d.dir(
                "lib",
                [
                    d.dir(
                        "src",
                        [d.file("transformer.dart", TRANSFORMER), d.file("primary.in", "")])])],
            pkg: ['barback']);

      var pub = pubRun(global: true, args: ["foo:script"]);

      pub.stdout.expect("generated");
      pub.shouldExit();
    });
  });
}