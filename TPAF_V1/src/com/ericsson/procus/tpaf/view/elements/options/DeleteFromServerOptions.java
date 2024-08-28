package com.ericsson.procus.tpaf.view.elements.options;

import java.util.ArrayList;
import java.util.HashMap;

import javafx.collections.ObservableList;
import javafx.scene.Node;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Dialogs;
import javafx.scene.control.Label;
import javafx.scene.control.Separator;
import javafx.scene.control.TextField;
import javafx.scene.control.Dialogs.DialogOptions;
import javafx.scene.control.Dialogs.DialogResponse;
import javafx.scene.layout.ColumnConstraints;
import javafx.scene.layout.ColumnConstraintsBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.VBox;
import javafx.util.Callback;

import com.ericsson.procus.tpaf.controller.TpViewController;
import com.ericsson.procus.tpaf.utils.CssHandler;
import com.ericsson.procus.tpaf.utils.TPAFenvironment;
import com.ericsson.procus.tpaf.view.View;

public class DeleteFromServerOptions {

	public static String[] tpOptions = { "Delete_Tech_Pack","Deactivate_Tech_Pack", "Delete_Tech_Pack_sets"};
	public static String[] IntfOptions = { "Delete_Interfaces", "Deactivate_Interfaces"};
	private View view;
	private TpViewController listener;

	private TextField location;
	private VBox tpDeleteBase, IntfDeleteBase;

	private HashMap<String, Object> results = new HashMap<String, Object>();

	public DeleteFromServerOptions(View view, TpViewController listener) {
		this.view = view;
		this.listener = listener;
	}

	public HashMap<String, Object> showOptionsWindow() {
		VBox base = new VBox();
		base.setSpacing(20);

		CssHandler css = new CssHandler();
		base.getStylesheets().add(css.getCssFileName());

		GridPane grid = new GridPane();
		grid.setHgap(10);
		grid.setVgap(10);

		location = new TextField();
		location.setPrefColumnCount(20);
		location.setPromptText("<ServerName>.athtem.eei.ericsson.se");

		grid.add(new Label("Server Name:"), 0, 0);
		grid.add(location, 1, 0);

		GridPane createOptions = new GridPane();
		createOptions.setVgap(10);
		createOptions.setHgap(10);
		ColumnConstraints widthconstraint = ColumnConstraintsBuilder.create()
				.percentWidth(50).build();
		createOptions.getColumnConstraints().addAll(widthconstraint,
				widthconstraint);

		tpDeleteBase = new VBox();
		tpDeleteBase.setSpacing(5);
		tpDeleteBase.getChildren().addAll(new Label("Tech Pack Options"),
				new Separator());
		for (String option : tpOptions) {
			CheckBox checker = new CheckBox(option.replace("_", " "));
			checker.setId(option);
			checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT,
					TPAFenvironment.SMALLFONT);
			checker.setOnAction(listener);
			tpDeleteBase.getChildren().addAll(checker);
		}

		IntfDeleteBase = new VBox();
		IntfDeleteBase.setSpacing(5);
		IntfDeleteBase.getChildren().addAll(new Label("Interface Options"),
				new Separator());
		for (String option : IntfOptions) {
			CheckBox checker = new CheckBox(option.replace("_", " "));
			checker.setId(option);
			checker.getStyleClass().addAll(TPAFenvironment.BLACKFONT,
					TPAFenvironment.SMALLFONT);
			checker.setOnAction(listener);
			IntfDeleteBase.getChildren().addAll(checker);
		}
		createOptions.getChildren().addAll(tpDeleteBase, IntfDeleteBase);
		GridPane.setConstraints(tpDeleteBase, 0, 0);
		GridPane.setConstraints(IntfDeleteBase, 1, 0);

		base.getChildren().addAll(grid, createOptions);

		DialogResponse resp = Dialogs.showCustomDialog(view.getStage(), base,
				"Please select the options", "Tech Pack Deletion",
				DialogOptions.OK_CANCEL, myCallback);

		if (resp == DialogResponse.CANCEL) {
			results.clear();
		}

		return results;
	}

	Callback<Void, Void> myCallback = new Callback<Void, Void>() {
		@Override
		public Void call(Void param) {
			if (location.getText().length() > 0) {
				results.put("ServerName", location.getText());
			}

			ArrayList<String> ticked = new ArrayList<String>();
			ObservableList<Node> list = tpDeleteBase.getChildren();
			for (Node node : list) {
				if (node instanceof CheckBox) {
					CheckBox cb = (CheckBox) node;
					if (cb.isSelected()) {
						ticked.add(cb.getId());
					}
				}
			}

			list = IntfDeleteBase.getChildren();
			for (Node node : list) {
				if (node instanceof CheckBox) {
					CheckBox cb = (CheckBox) node;
					if (cb.isSelected()) {
						ticked.add(cb.getId());
					}
				}
			}

			if (!ticked.isEmpty()) {
				results.put("Delete", ticked);
			}


			return null;
		}
	};

}
