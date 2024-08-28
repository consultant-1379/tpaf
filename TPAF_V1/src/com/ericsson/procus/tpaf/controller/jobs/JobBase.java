package com.ericsson.procus.tpaf.controller.jobs;

import javafx.concurrent.Task;

public class JobBase extends Task{
	
	@Override
	protected void scheduled(){
		super.scheduled();
	}
	
	@Override
	protected void running(){
		super.running();
	}
	
	@Override
	protected void succeeded(){
		super.succeeded();
	}
	
	@Override
	protected void failed(){
		super.failed();
	}
	
	@Override
	protected Object call() throws Exception {
		// TODO Auto-generated method stub
		return null;
	}

}
