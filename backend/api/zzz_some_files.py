

# def create_tags():
#    tags = [('red', Tag.Color.RED), ('green', Tag.Color.GREEN), ('blu', Tag.Color.BLUE)]
#    for name, color in tags:
#        Tag.objects.create(name=name, color=color)

# class Tag(models.Model):
#
#     class Color(models.IntegerChoices):
#         RED = 1
#         BLUE = 2
#         GREEN = 3
#
#     color_to_hex = {
#         Color.RED: '#yellow',
#         Color.BLUE: '#hhlhdf',
#         Color.GREEN: '#hdsfsf',
#     }
#
#     name = models.CharField(max_length=128)
#     color = models.PositiveSmallIntegerField(choices=Color.choices)
#
#     @property
#     def hex(self):
#         return Tag.color_to_hex[self.color]
#
#
# class TagSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model= Tag
#         fields = ['id', 'name', 'color', 'hex']
#         read_only_fields = ['hex']
#

# class Admin():
#  fields = ['id', 'name', 'color', 'hex']
#   readonly_fields = ['hex]
# POST /tags
# {
#     "color": 1,
#     "name": "user provided name",
# }
#
# GET
# /tags?name__contains='blablballba'
# /tags?name='dfldfd'
# /tags?color=1
# /tags?color=3&name='blablaba'
#
#
# Tag.objects.create(name='user-provided-name', color=Color.RED)


# class BoardForm(forms.ModelForm):
#     # необходимо добавить менеджер (чтобы учесть параметры создания кастомные)
#     class Meta:
#         model = Board
#         fields = ['dfssafdsfds']
#
#     def save(self, data):
#         self.cleaned_Data
#         self.request = user
#         boa

