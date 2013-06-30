#!/usr/bin/env bash

if [ -f config ]
then
	source config
else
	source config.sample
fi

FIDI_COMMAND="python fidibot.py"

if [[ "$FIDI_PASSWORD" != "" ]]
then
	FIDI_COMMAND+=" -x \"$FIDI_PASSWORD\""
fi

if [[ "$FIDI_REALNAME" != "" ]]
then
	FIDI_COMMAND+=" -r \"$FIDI_REALNAME\""
fi

if [[ "$FIDI_PORT" != "" ]]
then
	FIDI_COMMAND+=" -p $FIDI_PORT"
fi

FIDI_COMMAND+=" $FIDI_SERVER $FIDI_CHANNEL $FIDI_USERNAME"

for OPTION in "$@"
do
	if [[ "$OPTION" == -* ]]
	then
		FIDI_COMMAND+=" $OPTION"
	else
		FIDI_COMMAND+=" \"$OPTION\""
	fi
done

echo $FIDI_COMMAND
eval $FIDI_COMMAND
RET=$?

while [ $RET -gt 0 ]
do
	if [ $RET -eq 42 ]
	then
		echo "------------- Updating -------------"
		./install.sh update
	fi
	
	echo "------------ Restarting ------------"
	echo $FIDI_COMMAND
	eval $FIDI_COMMAND
	RET=$?
done
