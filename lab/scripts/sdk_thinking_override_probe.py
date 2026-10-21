"""Process-only SDK serializer probe for explicit request-level thinking flags.

Installed Python SDK declares prediction.raw but its KV converter rejects it.
This narrow shim handles only three boolean reasoning controls. No package,
defaults, prompts, output, native Chat history, permission or weights are edited.
"""
ALLOWED = {'llm.prediction.reasoning.enableThinking',
           'ext.virtualModel.customField.enableThinking',
           'ext.virtualModel.customField.preserveThinking'}


def install():
    import lmstudio._kv_config as kv
    original = kv._to_kv_config_stack_base

    def convert(config, keymap):
        if 'raw' not in config:
            return original(config, keymap)
        assert keymap is kv.TO_SERVER_PREDICTION
        stripped = dict(config)
        raw = stripped.pop('raw')
        assert isinstance(raw, dict) and set(raw) == {'fields'}
        fields = raw['fields']
        assert isinstance(fields, list)
        for field in fields:
            assert set(field) == {'key', 'value'} and field['key'] in ALLOWED
            assert isinstance(field['value'], bool)
        return original(stripped, keymap) + [dict(field) for field in fields]

    kv._to_kv_config_stack_base = convert
    return original


def validate():
    import lmstudio._kv_config as kv
    original = install()
    try:
        config = {'temperature': 0.2, 'maxTokens': 384,
                  'raw': {'fields': [{'key': 'llm.prediction.reasoning.enableThinking', 'value': False}]}}
        _, stack = kv.prediction_config_to_kv_config_stack(None, config)
        actual = stack.to_dict()['layers'][0]['config']['fields']
        assert {'key': 'llm.prediction.reasoning.enableThinking', 'value': False} in actual
        assert config['raw']['fields'][0]['value'] is False
        return actual
    finally:
        kv._to_kv_config_stack_base = original


if __name__ == '__main__':
    print(__import__('json').dumps({'serialized_request_fields': validate(), 'defaults_or_package_files_changed': False}))
