import pywapi
from basemodule import BaseModule, BaseCommandContext

from alternatives import _

class WeatherContext(BaseCommandContext):

    def cmd_keros_public(self, argument):
        """Gives The Temperature and Weather of Nafpaktos """

        #Get the weather for Nafpaktos
        nafpaktos = pywapi.get_weather_from_weather_com('GRXX1283:1')

        #Get the Current Weather
        curcond = nafpaktos.get('current_conditions')
        temp = curcond.get('temperature')
        text = curcond.get('text')
        time = curcond.get('last_updated')
        
        fmt_str = _("The Temperature is %s\nThe Weather is %s\nNafpaktos %s")
        target = self.channel
        self.send(target, fmt_str, temp, text, time)

    def cmd_kairos(self, argument):
        """Gives The Temperature and Weather of Nafpaktos """
        self.keros(argument)

class WeatherModule(BaseModule):
        context_class = WeatherContext

module = WeatherModule

