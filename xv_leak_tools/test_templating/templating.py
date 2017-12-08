import copy

from xv_leak_tools.log import L

# pylint: disable=too-few-public-methods

class Replacee:

    def __init__(self, placeholder_name):
        self.placeholder_name = placeholder_name

    def __str__(self):
        return "Replacee({})".format(self.placeholder_name)

class Replacement:

    def __init__(self):
        self.used = False

class Value(Replacement):

    def __init__(self, value):
        super().__init__()
        self.value = value

class Each(Replacement):

    def __init__(self, values):
        super().__init__()
        self.values = values

    def __iter__(self):
        return self.values.__iter__()

class TemplateEvaluator:

    @staticmethod
    def _explode_template_parameters(template_parameters):
        new_template_parameters_list = [template_parameters]

        keep_going = True
        while keep_going:
            keep_going = False
            template_parameters_list = new_template_parameters_list
            new_template_parameters_list = []
            for tps in template_parameters_list:
                for key, value in list(tps.items()):
                    if not isinstance(value, Each):
                        continue
                    for replacement_value in value:
                        new_template_parameters = copy.deepcopy(tps)
                        new_template_parameters[key] = replacement_value
                        new_template_parameters_list.append(new_template_parameters)
                    keep_going = True
                    break

        return template_parameters_list

    @staticmethod
    def _homogenise_template_parameters(template_parameters):
        template_parameters_list = TemplateEvaluator._explode_template_parameters(
            template_parameters)
        for tps in template_parameters_list:
            for key, value in list(tps.items()):
                if key[0] != '$' or isinstance(value, Value):
                    continue
                tps[key] = Value(value)
        return template_parameters_list

    @staticmethod
    def _replace_placeholder_in_list(the_list, template_parameters):
        for ivalue, value in enumerate(the_list):
            if isinstance(value, Replacee):
                replacement = template_parameters.get(value.placeholder_name, Value(None))
                replacement.used = True
                the_list[ivalue] = replacement.value
            else:
                TemplateEvaluator._replace_placeholder_in_container(value, template_parameters)

    @staticmethod
    def _replace_placeholder_in_dict(the_dict, template_parameters):
        for key, value in list(the_dict.items()):
            if isinstance(value, Replacee):
                replacement = template_parameters.get(value.placeholder_name, Value(None))
                replacement.used = True
                the_dict[key] = replacement.value
            else:
                TemplateEvaluator._replace_placeholder_in_container(value, template_parameters)

    @staticmethod
    def _replace_placeholder_in_container(item, template_parameters):
        # The only things we can handle are:
        #   * Dictionaries -> iterate elements
        #   * Lists -> iterate elements
        if isinstance(item, dict):
            return TemplateEvaluator._replace_placeholder_in_dict(item, template_parameters)
        elif isinstance(item, list):
            return TemplateEvaluator._replace_placeholder_in_list(item, template_parameters)
        return False

    @staticmethod
    def generate(template_parameters_list):
        # pylint is confused by the below code. It works correctly.
        # pylint: disable=invalid-sequence-index
        # pylint: disable=no-member

        simple_template_parameters_list = []
        for template_parameters in template_parameters_list:
            simple_template_parameters_list += TemplateEvaluator._homogenise_template_parameters(
                template_parameters)

        generated = []
        for template_parameters in simple_template_parameters_list:
            template = copy.deepcopy(template_parameters['TEMPLATE'])
            TemplateEvaluator._replace_placeholder_in_container(template, template_parameters)
            generated.append(template)

            for key, value in list(template_parameters.items()):
                if key[0] == '$' and not value.used:
                    L.warning("Placeholder {} was not used when evaluating template.".format(key))

        return generated
