package com.ericsson.procus.tpaf.iconCreator;

import javafx.application.Application;
import javafx.scene.effect.GaussianBlur;
import javafx.scene.effect.Reflection;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.Color;
import javafx.scene.paint.CycleMethod;
import javafx.scene.paint.LinearGradient;
import javafx.scene.paint.LinearGradientBuilder;
import javafx.scene.paint.RadialGradient;
import javafx.scene.paint.RadialGradientBuilder;
import javafx.scene.paint.Stop;
import javafx.scene.shape.Circle;
import javafx.scene.shape.CircleBuilder;
import javafx.scene.shape.Ellipse;
import javafx.scene.shape.EllipseBuilder;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.scene.Scene;
import jxl.format.Colour;

public class IconCreator extends Application {

	int radius = 200;
	
	@Override
	public void start(Stage primaryStage) {
		primaryStage.setTitle("TPAF Icon");
		StackPane root = new StackPane();
		root.setStyle("-fx-background-color: linear-gradient(to bottom, black, dodgerblue , transparent );");
		
		RadialGradient gradient1 = RadialGradientBuilder.create()
				.proportional(true)
				.centerX(0.5)
				.centerY(0.25)
				.stops(new Stop(0.0, Color.WHITE ), 
					new Stop(0.5, Color.rgb(255,255,255 , 0) ))
				.build();
		
		Ellipse ellipse = EllipseBuilder.create()
	             .centerY(0-radius/2)
	             .radiusX(radius/2.5)
	             .radiusY(radius/5)
	             .fill(gradient1)
	             .opacity(0.5)
	             .build();
		
		
		RadialGradient radial = RadialGradientBuilder.create()
				.proportional(true)
				.centerX(0.5)
				.centerY(0.45)
				.stops(new Stop(0.35, Color.TRANSPARENT ), 
					new Stop(0.95, Color.WHITE ))
				.build();
		
		
		LinearGradient linear = LinearGradientBuilder.create()
				.endX(0.5)
				.endY(1)
				.stops(new Stop(0.1, Color.RED ), 
					new Stop(0.2, Color.ORANGE ),
					new Stop(0.3, Color.YELLOW ),
					new Stop(0.4, Color.LIGHTGREEN ),
					new Stop(0.5, Color.DODGERBLUE ),
					new Stop(0.6, Color.PINK ),
					new Stop(0.7, Color.VIOLET ),
					new Stop(0.8, Color.WHITE ))
				.build();
		
		Circle circle = CircleBuilder.create()
				.radius(radius)
				.stroke(Color.WHITE)
				.fill(radial)
				.opacity(2)
				.build();
				
		
		
		Circle circle1 = CircleBuilder.create()
				.radius(radius)
				.fill(linear)
				.clip(circle)
				.build();
				
		Text name = new Text("TP AF");
		name.setFill(Color.WHITE);
		name.setStroke(Color.DODGERBLUE);
		name.setFont(Font.font("ERICSSON CAPITAL TT", FontWeight.THIN, 115));
		
		
		root.getChildren().addAll(circle1, name);

        primaryStage.setScene(new Scene(root, 500, 500));
        primaryStage.show();
	}

	public static void main(String[] args) {
		launch(args);
	}
}
