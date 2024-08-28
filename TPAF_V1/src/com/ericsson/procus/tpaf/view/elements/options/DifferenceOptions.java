package com.ericsson.procus.tpaf.view.elements.options;

import java.util.ArrayList;

import javafx.collections.ObservableList;
import javafx.scene.Node;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Dialogs;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.layout.VBox;
import javafx.util.Callback;

import com.ericsson.procus.tpaf.controller.TpViewController;
import com.ericsson.procus.tpaf.model.ModelInterface;
import com.ericsson.procus.tpaf.model.ModelManager;
import com.ericsson.procus.tpaf.utils.CssHandler;
import com.ericsson.procus.tpaf.view.View;

public class DifferenceOptions {

	private View view;
	private TpViewController listener;
	private ComboBox comboBox;
	private ModelInterface selectedModel = null;
	
	public DifferenceOptions(View view, TpViewController listener) {
		this.view = view;
		this.listener = listener;
	}

	public ModelInterface showOptionsWindow() {
		VBox base = new VBox();
		base.setSpacing(20);

		CssHandler css = new CssHandler();
		base.getStylesheets().add(css.getCssFileName());
		
		comboBox = new ComboBox(ModelManager.getInstance().getLoadedmodelInfo());
		comboBox.setValue("Select a model to compare against");
		
		base.getChildren().addAll(comboBox);
		
		DialogResponse resp = Dialogs.showCustomDialog(view.getStage(), base,
				"Please select the options", "Tech Pack Difference",
				DialogOptions.OK_CANCEL, myCallback);
		
		if (resp == DialogResponse.CANCEL) {
			selectedModel = null;
		}
		
		return selectedModel;
	}
	
	
	Callback<Void, Void> myCallback = new Callback<Void, Void>() {
		@Override
		public Void call(Void param) {
			if(comboBox.getSelectionModel().getSelectedItem() != "Select a model to compare against"){
				int item = comboBox.getSelectionModel().getSelectedIndex();
				selectedModel = ModelManager.getInstance().getFromList(item);
			}
			return null;
		}
	};
	
	
}
