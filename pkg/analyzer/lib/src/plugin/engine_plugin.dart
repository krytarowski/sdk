// Copyright (c) 2015, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

library analyzer.src.plugin.engine_plugin;

import 'package:analyzer/plugin/task.dart';
import 'package:analyzer/src/generated/engine.dart'
    show InternalAnalysisContext;
import 'package:analyzer/src/generated/error.dart' show AnalysisError;
import 'package:analyzer/src/task/dart.dart';
import 'package:analyzer/src/task/dart_work_manager.dart';
import 'package:analyzer/src/task/general.dart';
import 'package:analyzer/src/task/html.dart';
import 'package:analyzer/src/task/html_work_manager.dart';
import 'package:analyzer/task/model.dart';
import 'package:plugin/plugin.dart';

/**
 * A plugin that defines the extension points and extensions that are inherently
 * defined by the analysis engine.
 */
class EnginePlugin implements Plugin {
  /**
   * The simple identifier of the extension point that allows plugins to
   * register new analysis error results to compute for a Dart source.
   */
  static const String DART_ERRORS_FOR_SOURCE_EXTENSION_POINT =
      'dartErrorsForSource';

  /**
   * The simple identifier of the extension point that allows plugins to
   * register new analysis error results to compute for a Dart library
   * specific unit.
   */
  static const String DART_ERRORS_FOR_UNIT_EXTENSION_POINT =
      'dartErrorsForUnit';

  /**
   * The simple identifier of the extension point that allows plugins to
   * register new analysis error results to compute for an HTML source.
   */
  static const String HTML_ERRORS_EXTENSION_POINT = 'htmlErrors';

  /**
   * The simple identifier of the extension point that allows plugins to
   * register new analysis tasks with the analysis engine.
   */
  static const String TASK_EXTENSION_POINT = 'task';

  /**
   * The simple identifier of the extension point that allows plugins to
   * register new work manager factories with the analysis engine.
   */
  static const String WORK_MANAGER_FACTORY_EXTENSION_POINT =
      'workManagerFactory';

  /**
   * The unique identifier of this plugin.
   */
  static const String UNIQUE_IDENTIFIER = 'analysis_engine.core';

  /**
   * The extension point that allows plugins to register new analysis error
   * results for a Dart source.
   */
  ExtensionPoint dartErrorsForSourceExtensionPoint;

  /**
   * The extension point that allows plugins to register new analysis error
   * results for a Dart library specific unit.
   */
  ExtensionPoint dartErrorsForUnitExtensionPoint;

  /**
   * The extension point that allows plugins to register new analysis error
   * results for an HTML source.
   */
  ExtensionPoint htmlErrorsExtensionPoint;

  /**
   * The extension point that allows plugins to register new analysis tasks with
   * the analysis engine.
   */
  ExtensionPoint taskExtensionPoint;

  /**
   * The extension point that allows plugins to register new work manager
   * factories with the analysis engine.
   */
  ExtensionPoint workManagerFactoryExtensionPoint;

  /**
   * Initialize a newly created plugin.
   */
  EnginePlugin();

  /**
   * Return a list containing all of the contributed analysis error result
   * descriptors for Dart sources.
   */
  @ExtensionPointId('DART_ERRORS_FOR_SOURCE_EXTENSION_POINT_ID')
  List<TaskDescriptor> get dartErrorsForSource =>
      dartErrorsForSourceExtensionPoint.extensions;

  /**
   * Return a list containing all of the contributed analysis error result
   * descriptors for Dart library specific units.
   */
  @ExtensionPointId('DART_ERRORS_FOR_UNIT_EXTENSION_POINT_ID')
  List<TaskDescriptor> get dartErrorsForUnit =>
      dartErrorsForUnitExtensionPoint.extensions;

  /**
   * Return a list containing all of the contributed analysis error result
   * descriptors for HTML sources.
   */
  @ExtensionPointId('HTML_ERRORS_EXTENSION_POINT_ID')
  List<TaskDescriptor> get htmlErrors => htmlErrorsExtensionPoint.extensions;

  /**
   * Return a list containing all of the task descriptors that were contributed.
   */
  List<TaskDescriptor> get taskDescriptors => taskExtensionPoint.extensions;

  @override
  String get uniqueIdentifier => UNIQUE_IDENTIFIER;

  /**
   * Return a list containing all of the work manager factories that were
   * contributed.
   */
  List<WorkManagerFactory> get workManagerFactories =>
      workManagerFactoryExtensionPoint.extensions;

  @override
  void registerExtensionPoints(RegisterExtensionPoint registerExtensionPoint) {
    dartErrorsForSourceExtensionPoint = registerExtensionPoint(
        DART_ERRORS_FOR_SOURCE_EXTENSION_POINT,
        _validateAnalysisErrorListResultDescriptor);
    dartErrorsForUnitExtensionPoint = registerExtensionPoint(
        DART_ERRORS_FOR_UNIT_EXTENSION_POINT,
        _validateAnalysisErrorListResultDescriptor);
    htmlErrorsExtensionPoint = registerExtensionPoint(
        HTML_ERRORS_EXTENSION_POINT,
        _validateAnalysisErrorListResultDescriptor);
    taskExtensionPoint =
        registerExtensionPoint(TASK_EXTENSION_POINT, _validateTaskExtension);
    workManagerFactoryExtensionPoint = registerExtensionPoint(
        WORK_MANAGER_FACTORY_EXTENSION_POINT,
        _validateWorkManagerFactoryExtension);
  }

  @override
  void registerExtensions(RegisterExtension registerExtension) {
    _registerTaskExtensions(registerExtension);
    _registerWorkManagerFactoryExtensions(registerExtension);
    _registerDartErrorsForSource(registerExtension);
    _registerDartErrorsForUnit(registerExtension);
    _registerHtmlErrors(registerExtension);
  }

  void _registerDartErrorsForSource(RegisterExtension registerExtension) {
    registerExtension(DART_ERRORS_FOR_SOURCE_EXTENSION_POINT_ID, PARSE_ERRORS);
    registerExtension(DART_ERRORS_FOR_SOURCE_EXTENSION_POINT_ID, SCAN_ERRORS);
  }

  void _registerDartErrorsForUnit(RegisterExtension registerExtension) {
    registerExtension(
        DART_ERRORS_FOR_UNIT_EXTENSION_POINT_ID, LIBRARY_UNIT_ERRORS);
  }

  void _registerHtmlErrors(RegisterExtension registerExtension) {
    registerExtension(HTML_ERRORS_EXTENSION_POINT_ID, HTML_DOCUMENT_ERRORS);
  }

  void _registerTaskExtensions(RegisterExtension registerExtension) {
    String taskId = TASK_EXTENSION_POINT_ID;
    //
    // Register general tasks.
    //
    registerExtension(taskId, GetContentTask.DESCRIPTOR);
    //
    // Register Dart tasks.
    //
    registerExtension(taskId, BuildCompilationUnitElementTask.DESCRIPTOR);
    registerExtension(taskId, BuildDirectiveElementsTask.DESCRIPTOR);
    registerExtension(taskId, BuildEnumMemberElementsTask.DESCRIPTOR);
    registerExtension(taskId, BuildExportNamespaceTask.DESCRIPTOR);
    registerExtension(taskId, BuildLibraryElementTask.DESCRIPTOR);
    registerExtension(taskId, BuildPublicNamespaceTask.DESCRIPTOR);
    registerExtension(taskId, BuildSourceExportClosureTask.DESCRIPTOR);
    registerExtension(taskId, BuildSourceImportExportClosureTask.DESCRIPTOR);
    registerExtension(taskId, BuildTypeProviderTask.DESCRIPTOR);
    registerExtension(taskId, ComputeConstantDependenciesTask.DESCRIPTOR);
    registerExtension(taskId, ComputeConstantValueTask.DESCRIPTOR);
    registerExtension(
        taskId, ComputeInferableStaticVariableDependenciesTask.DESCRIPTOR);
    registerExtension(taskId, ComputeLibraryCycleTask.DESCRIPTOR);
    registerExtension(taskId, ContainingLibrariesTask.DESCRIPTOR);
    registerExtension(taskId, DartErrorsTask.DESCRIPTOR);
    registerExtension(taskId, EvaluateUnitConstantsTask.DESCRIPTOR);
    registerExtension(taskId, GatherUsedImportedElementsTask.DESCRIPTOR);
    registerExtension(taskId, GatherUsedLocalElementsTask.DESCRIPTOR);
    registerExtension(taskId, GenerateHintsTask.DESCRIPTOR);
    registerExtension(taskId, GenerateLintsTask.DESCRIPTOR);
    registerExtension(taskId, InferInstanceMembersInUnitTask.DESCRIPTOR);
    registerExtension(taskId, InferStaticVariableTypesInUnitTask.DESCRIPTOR);
    registerExtension(taskId, InferStaticVariableTypeTask.DESCRIPTOR);
    registerExtension(taskId, LibraryErrorsReadyTask.DESCRIPTOR);
    registerExtension(taskId, LibraryUnitErrorsTask.DESCRIPTOR);
    registerExtension(taskId, ParseDartTask.DESCRIPTOR);
    registerExtension(taskId, PartiallyResolveUnitReferencesTask.DESCRIPTOR);
    registerExtension(taskId, ResolveInstanceFieldsInUnitTask.DESCRIPTOR);
    registerExtension(taskId, ResolveLibraryReferencesTask.DESCRIPTOR);
    registerExtension(taskId, ResolveLibraryTypeNamesTask.DESCRIPTOR);
    registerExtension(taskId, ResolveUnitTask.DESCRIPTOR);
    registerExtension(taskId, ResolveUnitTypeNamesTask.DESCRIPTOR);
    registerExtension(taskId, ResolveVariableReferencesTask.DESCRIPTOR);
    registerExtension(taskId, ScanDartTask.DESCRIPTOR);
    registerExtension(taskId, VerifyUnitTask.DESCRIPTOR);
    //
    // Register HTML tasks.
    //
    registerExtension(taskId, DartScriptsTask.DESCRIPTOR);
    registerExtension(taskId, HtmlErrorsTask.DESCRIPTOR);
    registerExtension(taskId, ParseHtmlTask.DESCRIPTOR);
  }

  void _registerWorkManagerFactoryExtensions(
      RegisterExtension registerExtension) {
    String taskId = WORK_MANAGER_EXTENSION_POINT_ID;
    registerExtension(taskId,
        (InternalAnalysisContext context) => new DartWorkManager(context));
    registerExtension(taskId,
        (InternalAnalysisContext context) => new HtmlWorkManager(context));
  }

  /**
   * Validate the given extension by throwing an [ExtensionError] if it is not
   * a [ListResultDescriptor] of [AnalysisError]s.
   */
  void _validateAnalysisErrorListResultDescriptor(Object extension) {
    if (extension is! ListResultDescriptor<AnalysisError>) {
      String id = taskExtensionPoint.uniqueIdentifier;
      throw new ExtensionError(
          'Extensions to $id must be a ListResultDescriptor<AnalysisError>');
    }
  }

  /**
   * Validate the given extension by throwing an [ExtensionError] if it is not
   * a [TaskDescriptor].
   */
  void _validateTaskExtension(Object extension) {
    if (extension is! TaskDescriptor) {
      String id = taskExtensionPoint.uniqueIdentifier;
      throw new ExtensionError('Extensions to $id must be a TaskDescriptor');
    }
  }

  /**
   * Validate the given extension by throwing an [ExtensionError] if it is not
   * a [WorkManagerFactory].
   */
  void _validateWorkManagerFactoryExtension(Object extension) {
    if (extension is! WorkManagerFactory) {
      String id = taskExtensionPoint.uniqueIdentifier;
      throw new ExtensionError(
          'Extensions to $id must be a WorkManagerFactory');
    }
  }
}

/**
 * Annotation describing the relationship between a getter in [EnginePlugin]
 * and the associated identifier (in '../../plugin/task.dart') which can be
 * passed to the extension manager to populate it.
 *
 * This annotation is not used at runtime; it is used to aid in static analysis
 * of the task model during development.
 */
class ExtensionPointId {
  final String extensionPointId;

  const ExtensionPointId(this.extensionPointId);
}
