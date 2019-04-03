"""
All exception classes are defined here
"""
class DYCError(Exception): pass
class SetupError(DYCError): pass
class UndefinedPattern(DYCError): pass
class ConfigurationMissing(Exception): pass
class FormattingConfigurationHandler(ConfigurationMissing): pass
class QuitConfirmEditor(DYCError): pass
class DYCConfigurationSetup(DYCError): pass
class OverrideConfigurations(DYCError): pass