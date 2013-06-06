import pywapi
from basemodule import BaseModule, BaseCommandContext

from alternatives import _

class WeatherContext(BaseCommandContext):

    def cmd_keros(self, argument):
        """Gives The Temperature and Weather of Nafpaktos """
        target = self.channel if self.channel.startswith("#") else self.nick
        
        # Get the weather for Nafpaktos
        nafpaktos = pywapi.get_weather_from_weather_com('GRXX1283:1')
        
        # Check for errors
        error = nafpaktos.get('error')
        if error:
            self.logger.error(error)
            self.send(target, _("Error retrieving data: %s"), error)
            return
        
        # Get the Current Weather
        curcond = nafpaktos.get('current_conditions', {})
        temp = curcond.get('temperature')
        text = curcond.get('text')
        time = curcond.get('last_updated')
        
        fmt_str = _("The Temperature is %s\nThe Weather is %s\nNafpaktos %s")
        self.send(target, fmt_str, temp, _(text), time)

    def cmd_kairos(self, argument):
        """Gives The Temperature and Weather of Nafpaktos """
        self.cmd_keros(argument)

class WeatherModule(BaseModule):
        context_class = WeatherContext

module = WeatherModule
