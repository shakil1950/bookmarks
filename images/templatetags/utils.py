from django import template

register = template.Library()

@register.filter
def number_format(num):
    if num is None:
        return "0"
    num = float(num)
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # ১০০০ এর নিচে হলে সরাসরি সংখ্যা দেখাবে, উপরে হলে k, M যোগ করবে
    return '{}{}'.format('{:g}'.format(float('{:.1f}'.format(num))), ['', 'k', 'M', 'G', 'T', 'P'][magnitude])