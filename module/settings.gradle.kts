pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
        maven { url = uri("https://nexus.inductiveautomation.com/repository/public/") }
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories {
        mavenCentral()
        maven { url = uri("https://nexus.inductiveautomation.com/repository/public/") }
    }
}

enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")

// Cadre HMI Components module (spike): pinned web components as Perspective components.
rootProject.name = "cadre-openbridge"
include(":gateway", ":common", ":designer")
