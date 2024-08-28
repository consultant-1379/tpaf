package com.ericsson.procus.tpaf.controller;

import com.ericsson.procus.tpaf.model.ModelFactory;
import com.ericsson.procus.tpaf.view.View;

import javafx.event.Event;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;

public class JobController implements Controller{

	private View view;
	private ModelFactory modelcreator;
	public JobController(ModelFactory modelcreator, View view){
		this.view = view;
		this.modelcreator = modelcreator;
	}

	@Override
	public void handle(Event event) {
		Text e = (Text)event.getSource();
		String VboxID = e.getId().split("_")[0];
		VBox vbox = (VBox)view.lookup("#"+VboxID);
		vbox.getChildren().remove(0, vbox.getChildren().size());
	}
	
	@Override
	public void execute() {}

}
