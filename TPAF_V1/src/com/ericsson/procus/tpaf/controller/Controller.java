package com.ericsson.procus.tpaf.controller;

import javafx.event.Event;
import javafx.event.EventHandler;

public interface Controller extends EventHandler{
		
	public void execute();
	@Override
	public void handle(Event event);


}
